#pragma once

#include <string>
#include <sstream>
#include <Poco/UUID.h>
#include <Poco/UUIDGenerator.h>
#include <Poco/Timestamp.h>
#include <Poco/JSON/Object.h>
#include <Poco/JSON/Stringifier.h>

namespace FitnessTracker {
namespace Events {

class Event {
public:
    Event(const std::string& eventType,
          const std::string& aggregateId,
          const std::string& aggregateType)
        : eventId_(Poco::UUIDGenerator::defaultGenerator().createRandom().toString())
        , eventType_(eventType)
        , timestamp_(Poco::Timestamp())
        , aggregateId_(aggregateId)
        , aggregateType_(aggregateType)
    {}

    virtual ~Event() = default;

    std::string eventId() const { return eventId_; }
    std::string eventType() const { return eventType_; }
    Poco::Timestamp timestamp() const { return timestamp_; }
    std::string aggregateId() const { return aggregateId_; }
    std::string aggregateType() const { return aggregateType_; }

    virtual Poco::JSON::Object::Ptr payload() const = 0;

    std::string toJson() const {
        Poco::JSON::Object::Ptr root = new Poco::JSON::Object;
        root->set("event_id", eventId_);
        root->set("event_type", eventType_);
        root->set("timestamp", static_cast<double>(timestamp_.epochMicroseconds()) / 1000);
        root->set("aggregate_id", aggregateId_);
        root->set("aggregate_type", aggregateType_);
        root->set("payload", payload());

        std::ostringstream oss;
        Poco::JSON::Stringifier::stringify(root, oss);
        return oss.str();
    }

protected:
    std::string eventId_;
    std::string eventType_;
    Poco::Timestamp timestamp_;
    std::string aggregateId_;
    std::string aggregateType_;
};

}  // namespace Events
}  // namespace FitnessTracker
