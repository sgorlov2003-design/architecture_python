#include "events/kafka_producer.h"
#include <librdkafka/rdkafkacpp.h>
#include <Poco/Format.h>
#include <Poco/JSON/Parser.h>
#include <Poco/Logger.h>
#include <stdexcept>

namespace FitnessTracker {
namespace Events {

class KafkaProducer::DeliveryReportCb : public RdKafka::DeliveryReportCb {
public:
    void dr_cb(RdKafka::Message& msg) override {
        if (msg.err() != RdKafka::ERR_NO_ERROR) {
            Poco::Logger::get("KafkaProducer").error(
                Poco::format("Delivery failed: %s", msg.errstr()));
        }
    }
};

KafkaProducer::KafkaProducer(const std::string& brokers, const std::string& topic)
    : brokers_(brokers)
    , topicName_(topic)
{
    std::string errstr;

    conf_.reset(RdKafka::Conf::create(RdKafka::Conf::CONF_GLOBAL));
    topicConf_.reset(RdKafka::Conf::create(RdKafka::Conf::CONF_TOPIC));

    conf_->set("bootstrap.servers", brokers_, errstr);
    conf_->set("enable.idempotence", "true", errstr);
    conf_->set("acks", "all", errstr);
    conf_->set("retries", "5", errstr);
    conf_->set("message.timeout.ms", "30000", errstr);

    deliveryReporter_.reset(new DeliveryReportCb);
    conf_->set("dr_cb", deliveryReporter_.get(), errstr);

    producer_.reset(RdKafka::Producer::create(conf_.get(), errstr));
    if (!producer_) {
        throw std::runtime_error("Failed to create producer: " + errstr);
    }

    topic_.reset(RdKafka::Topic::create(producer_.get(), topicName_, topicConf_.get(), errstr));
    if (!topic_) {
        throw std::runtime_error("Failed to create topic: " + errstr);
    }

    Poco::Logger::get("KafkaProducer").information(
        Poco::format("Kafka producer initialized: %s / %s", brokers_, topicName_));
}

KafkaProducer::~KafkaProducer()
{
    if (producer_) {
        producer_->flush(10000);
    }
}

std::string KafkaProducer::partitionKey(const Event& event)
{
    Poco::JSON::Parser parser;
    auto parsed = parser.parse(event.toJson()).extract<Poco::JSON::Object::Ptr>();
    auto payload = parsed->getObject("payload");

    if (payload && payload->has("user_id")) {
        return payload->getValue<std::string>("user_id");
    }
    return event.aggregateId();
}

bool KafkaProducer::publish(const Event& event)
{
    std::string key = partitionKey(event);
    std::string payload = event.toJson();

    RdKafka::ErrorCode resp = producer_->produce(
        topic_.get(),
        RdKafka::Topic::PARTITION_UA,
        RdKafka::Producer::RK_MSG_COPY,
        const_cast<char*>(payload.c_str()),
        payload.size(),
        key.empty() ? nullptr : const_cast<char*>(key.c_str()),
        key.size(),
        nullptr);

    if (resp != RdKafka::ERR_NO_ERROR) {
        Poco::Logger::get("KafkaProducer").error(
            Poco::format("Failed to produce: %s", RdKafka::err2str(resp)));
        return false;
    }

    producer_->poll(0);
    return true;
}

}  // namespace Events
}  // namespace FitnessTracker
