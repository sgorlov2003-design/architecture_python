#pragma once

#include <memory>
#include <string>
#include "event.h"

namespace RdKafka {
class Conf;
class Producer;
class Topic;
}  // namespace RdKafka

namespace FitnessTracker {
namespace Events {

class KafkaProducer {
public:
    KafkaProducer(const std::string& brokers, const std::string& topic);
    ~KafkaProducer();

    bool publish(const Event& event);

private:
    std::string partitionKey(const Event& event);

    class DeliveryReportCb;
    std::unique_ptr<DeliveryReportCb> deliveryReporter_;
    std::unique_ptr<RdKafka::Conf> conf_;
    std::unique_ptr<RdKafka::Conf> topicConf_;
    std::unique_ptr<RdKafka::Producer> producer_;
    std::unique_ptr<RdKafka::Topic> topic_;
    std::string brokers_;
    std::string topicName_;
};

}  // namespace Events
}  // namespace FitnessTracker
