#include "events/kafka_consumer.h"
#include <iostream>
#include <iterator>
#include <librdkafka/rdkafkacpp.h>
#include <Poco/Format.h>
#include <Poco/JSON/Parser.h>
#include <Poco/Logger.h>
#include <stdexcept>

namespace FitnessTracker {
namespace Events {

class KafkaConsumer::EventHandlerCb : public RdKafka::EventCb {
public:
    void event_cb(RdKafka::Event& event) override
    {
        if (event.type() == RdKafka::Event::EVENT_ERROR) {
            Poco::Logger::get("KafkaConsumer").error(
                Poco::format("Kafka error: %s", event.str()));
        }
    }
};

KafkaConsumer::KafkaConsumer(const std::string& brokers,
                             const std::string& topic,
                             const std::string& groupId)
    : brokers_(brokers)
    , topic_(topic)
    , groupId_(groupId)
    , running_(false)
{
    std::string errstr;

    conf_.reset(RdKafka::Conf::create(RdKafka::Conf::CONF_GLOBAL));
    conf_->set("bootstrap.servers", brokers_, errstr);
    conf_->set("group.id", groupId_, errstr);
    conf_->set("enable.auto.commit", "false", errstr);
    conf_->set("auto.offset.reset", "earliest", errstr);

    eventHandler_.reset(new EventHandlerCb);
    conf_->set("event_cb", eventHandler_.get(), errstr);

    consumer_.reset(RdKafka::KafkaConsumer::create(conf_.get(), errstr));
    if (!consumer_) {
        throw std::runtime_error("Failed to create consumer: " + errstr);
    }

    std::vector<std::string> topics = {topic_};
    RdKafka::ErrorCode resp = consumer_->subscribe(topics);
    if (resp != RdKafka::ERR_NO_ERROR) {
        throw std::runtime_error("Subscribe failed: " + RdKafka::err2str(resp));
    }

    Poco::Logger::get("KafkaConsumer").information(
        Poco::format("Consumer subscribed: %s (group: %s)", topic_, groupId_));
}

KafkaConsumer::~KafkaConsumer()
{
    stop();
}

void KafkaConsumer::start()
{
    running_ = true;
    consumerThread_ = std::thread(&KafkaConsumer::consumeLoop, this);
}

void KafkaConsumer::stop()
{
    running_ = false;
    if (consumerThread_.joinable()) {
        consumerThread_.join();
    }
    if (consumer_) {
        consumer_->close();
    }
}

void KafkaConsumer::consumeLoop()
{
    while (running_) {
        RdKafka::Message* msg = consumer_->consume(1000);

        switch (msg->err()) {
            case RdKafka::ERR__TIMED_OUT:
                break;
            case RdKafka::ERR_NO_ERROR:
                processMessage(msg);
                consumer_->commitAsync(msg);
                break;
            case RdKafka::ERR__PARTITION_EOF:
                break;
            default:
                if (msg->err() == RdKafka::ERR__FATAL) {
                    std::string err;
                    consumer_->fatal_error(err);
                    Poco::Logger::get("KafkaConsumer").critical(
                        Poco::format("Fatal: %s", err));
                    running_ = false;
                }
                break;
        }
        delete msg;
    }
}

void KafkaConsumer::processMessage(RdKafka::Message* msg)
{
    if (!msg->payload()) {
        return;
    }

    std::string payloadStr(static_cast<char*>(msg->payload()), msg->len());

    try {
        Poco::JSON::Parser parser;
        auto eventJson = parser.parse(payloadStr).extract<Poco::JSON::Object::Ptr>();

        std::string eventType = eventJson->getValue<std::string>("event_type");
        std::string eventId = eventJson->getValue<std::string>("event_id");

        if (isDuplicate(eventId)) {
            return;
        }

        if (eventType == "UserRegistered") {
            handleUserRegistered(eventJson);
        } else if (eventType == "ExerciseCreated") {
            handleExerciseCreated(eventJson);
        } else if (eventType == "ExerciseUpdated") {
            handleExerciseUpdated(eventJson);
        } else if (eventType == "WorkoutCreated") {
            handleWorkoutCreated(eventJson);
        } else if (eventType == "ExerciseAddedToWorkout") {
            handleExerciseAddedToWorkout(eventJson);
        } else {
            Poco::Logger::get("KafkaConsumer").warning(
                Poco::format("Unknown event type: %s", eventType));
        }

        markProcessed(eventId);
    } catch (...) {
        Poco::Logger::get("KafkaConsumer").error("Failed to parse event");
    }
}

bool KafkaConsumer::isDuplicate(const std::string& eventId)
{
    std::lock_guard<std::mutex> lock(processedMutex_);
    return processedEvents_.find(eventId) != processedEvents_.end();
}

void KafkaConsumer::markProcessed(const std::string& eventId)
{
    std::lock_guard<std::mutex> lock(processedMutex_);
    processedEvents_.insert(eventId);
    if (processedEvents_.size() > 10000) {
        auto it = processedEvents_.begin();
        std::advance(it, static_cast<long>(processedEvents_.size() / 2));
        processedEvents_.erase(processedEvents_.begin(), it);
    }
}

void KafkaConsumer::handleUserRegistered(Poco::JSON::Object::Ptr eventJson)
{
    auto payload = eventJson->getObject("payload");
    std::string userId = payload->getValue<std::string>("user_id");
    std::string login = payload->getValue<std::string>("login");
    Poco::Logger::get("KafkaConsumer").information(
        Poco::format("Processed UserRegistered: %s (login: %s)", userId, login));
    std::cout << "[consumer] UserRegistered user_id=" << userId << " login=" << login << std::endl;
}

void KafkaConsumer::handleExerciseCreated(Poco::JSON::Object::Ptr eventJson)
{
    auto payload = eventJson->getObject("payload");
    std::string exerciseId = payload->getValue<std::string>("exercise_id");
    std::string name = payload->getValue<std::string>("name");
    Poco::Logger::get("KafkaConsumer").information(
        Poco::format("Processed ExerciseCreated: %s (%s)", exerciseId, name));
    std::cout << "[consumer] ExerciseCreated id=" << exerciseId << " name=" << name << std::endl;
}

void KafkaConsumer::handleExerciseUpdated(Poco::JSON::Object::Ptr eventJson)
{
    auto payload = eventJson->getObject("payload");
    std::string exerciseId = payload->getValue<std::string>("exercise_id");
    Poco::Logger::get("KafkaConsumer").information(
        Poco::format("Processed ExerciseUpdated: %s", exerciseId));
}

void KafkaConsumer::handleWorkoutCreated(Poco::JSON::Object::Ptr eventJson)
{
    auto payload = eventJson->getObject("payload");
    std::string workoutId = payload->getValue<std::string>("workout_id");
    std::string name = payload->getValue<std::string>("name");
    Poco::Logger::get("KafkaConsumer").information(
        Poco::format("Processed WorkoutCreated: %s (%s)", workoutId, name));
    std::cout << "[consumer] WorkoutCreated id=" << workoutId << " name=" << name << std::endl;
}

void KafkaConsumer::handleExerciseAddedToWorkout(Poco::JSON::Object::Ptr eventJson)
{
    auto payload = eventJson->getObject("payload");
    std::string workoutId = payload->getValue<std::string>("workout_id");
    std::string exerciseId = payload->getValue<std::string>("exercise_id");
    Poco::Logger::get("KafkaConsumer").information(
        Poco::format("Processed ExerciseAddedToWorkout: workout=%s exercise=%s",
                     workoutId,
                     exerciseId));
    std::cout << "[consumer] ExerciseAddedToWorkout workout=" << workoutId
              << " exercise=" << exerciseId << std::endl;
}

}  // namespace Events
}  // namespace FitnessTracker
