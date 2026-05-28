#include "events/fitness_events.h"
#include "events/kafka_consumer.h"
#include "events/kafka_producer.h"
#include <Poco/AutoPtr.h>
#include <Poco/ConsoleChannel.h>
#include <Poco/Format.h>
#include <Poco/FormattingChannel.h>
#include <Poco/Logger.h>
#include <Poco/PatternFormatter.h>
#include <Poco/UUIDGenerator.h>
#include <chrono>
#include <cstdlib>
#include <iostream>
#include <thread>

using namespace FitnessTracker::Events;

static std::string envOr(const char* name, const char* fallback)
{
    const char* v = std::getenv(name);
    return (v && v[0]) ? std::string(v) : std::string(fallback);
}

int main()
{
    Poco::AutoPtr<Poco::ConsoleChannel> console(new Poco::ConsoleChannel);
    Poco::AutoPtr<Poco::PatternFormatter> formatter(new Poco::PatternFormatter);
    Poco::AutoPtr<Poco::FormattingChannel> channel(new Poco::FormattingChannel(formatter, console));
    Poco::Logger::root().setChannel(channel);
    Poco::Logger::root().setLevel(Poco::Message::PRIO_INFORMATION);

    const std::string brokers = envOr("KAFKA_BROKERS", "kafka:29092");
    const std::string topic = envOr("KAFKA_TOPIC", "fitness_tracker_events");
    const std::string groupId = envOr("KAFKA_GROUP_ID", "fitness_events_demo");

    auto& log = Poco::Logger::get("FitnessDemo");
    log.information(Poco::format("Starting fitness events demo (brokers=%s, topic=%s)",
                                 brokers,
                                 topic));

    KafkaConsumer consumer(brokers, topic, groupId);
    consumer.start();

    std::this_thread::sleep_for(std::chrono::seconds(3));

    KafkaProducer producer(brokers, topic);

    auto& gen = Poco::UUIDGenerator::defaultGenerator();
    const std::string userId = gen.createRandom().toString();
    const std::string exerciseId = gen.createRandom().toString();
    const std::string workoutId = gen.createRandom().toString();

    UserRegistered userEvent(userId, "athlete01", "Степан", "Горлов");
    ExerciseCreated exerciseEvent(exerciseId, userId, "Отжимания", "силовые");
    WorkoutCreated workoutEvent(workoutId, userId, "Утренняя тренировка", "2025-05-28");
    ExerciseAddedToWorkout linkEvent(workoutId, exerciseId, userId, 3, 15);
    ExerciseUpdated updateEvent(exerciseId, userId, {"name"}, "Отжимания с упором");

    struct PublishItem {
        const char* label;
        const Event& event;
    };

    PublishItem items[] = {
        {"UserRegistered", userEvent},
        {"ExerciseCreated", exerciseEvent},
        {"WorkoutCreated", workoutEvent},
        {"ExerciseAddedToWorkout", linkEvent},
        {"ExerciseUpdated", updateEvent},
    };

    for (const auto& item : items) {
        if (!producer.publish(item.event)) {
            log.error(Poco::format("Failed to publish %s", std::string(item.label)));
            return 1;
        }
        log.information(Poco::format("Published %s", std::string(item.label)));
        std::cout << "[demo] Published " << item.label << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }

    log.information("Waiting for consumer to process events...");
    std::cout << "[demo] Waiting for consumer..." << std::endl;
    std::this_thread::sleep_for(std::chrono::seconds(8));

    consumer.stop();
    log.information("Demo finished successfully");
    std::cout << "[demo] Finished successfully" << std::endl;
    return 0;
}
