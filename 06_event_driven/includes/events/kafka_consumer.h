#pragma once

#include <atomic>
#include <memory>
#include <mutex>
#include <string>
#include <thread>
#include <unordered_set>
#include <Poco/JSON/Object.h>

namespace RdKafka {
class Conf;
class KafkaConsumer;
class Message;
}  // namespace RdKafka

namespace FitnessTracker {
namespace Events {

class KafkaConsumer {
public:
    KafkaConsumer(const std::string& brokers,
                  const std::string& topic,
                  const std::string& groupId);
    ~KafkaConsumer();

    void start();
    void stop();

private:
    void consumeLoop();
    void processMessage(RdKafka::Message* msg);

    bool isDuplicate(const std::string& eventId);
    void markProcessed(const std::string& eventId);

    void handleUserRegistered(Poco::JSON::Object::Ptr eventJson);
    void handleExerciseCreated(Poco::JSON::Object::Ptr eventJson);
    void handleExerciseUpdated(Poco::JSON::Object::Ptr eventJson);
    void handleWorkoutCreated(Poco::JSON::Object::Ptr eventJson);
    void handleExerciseAddedToWorkout(Poco::JSON::Object::Ptr eventJson);

    class EventHandlerCb;
    std::unique_ptr<EventHandlerCb> eventHandler_;
    std::unique_ptr<RdKafka::Conf> conf_;
    std::unique_ptr<RdKafka::KafkaConsumer> consumer_;
    std::string brokers_;
    std::string topic_;
    std::string groupId_;
    std::atomic<bool> running_;
    std::thread consumerThread_;
    std::unordered_set<std::string> processedEvents_;
    std::mutex processedMutex_;
};

}  // namespace Events
}  // namespace FitnessTracker
