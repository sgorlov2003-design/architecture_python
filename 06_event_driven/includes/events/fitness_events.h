#pragma once

#include "event.h"
#include <Poco/JSON/Object.h>
#include <Poco/JSON/Array.h>
#include <vector>

namespace FitnessTracker {
namespace Events {

class UserRegistered : public Event {
public:
    UserRegistered(const std::string& userId,
                   const std::string& login,
                   const std::string& firstName,
                   const std::string& lastName)
        : Event("UserRegistered", userId, "User")
        , userId_(userId)
        , login_(login)
        , firstName_(firstName)
        , lastName_(lastName)
    {}

    Poco::JSON::Object::Ptr payload() const override {
        Poco::JSON::Object::Ptr p = new Poco::JSON::Object;
        p->set("user_id", userId_);
        p->set("login", login_);
        p->set("first_name", firstName_);
        p->set("last_name", lastName_);
        return p;
    }

private:
    std::string userId_, login_, firstName_, lastName_;
};

class ExerciseCreated : public Event {
public:
    ExerciseCreated(const std::string& exerciseId,
                    const std::string& userId,
                    const std::string& name,
                    const std::string& category = "")
        : Event("ExerciseCreated", exerciseId, "Exercise")
        , exerciseId_(exerciseId)
        , userId_(userId)
        , name_(name)
        , category_(category)
    {}

    Poco::JSON::Object::Ptr payload() const override {
        Poco::JSON::Object::Ptr p = new Poco::JSON::Object;
        p->set("exercise_id", exerciseId_);
        p->set("user_id", userId_);
        p->set("name", name_);
        if (!category_.empty()) {
            p->set("category", category_);
        }
        return p;
    }

private:
    std::string exerciseId_, userId_, name_, category_;
};

class ExerciseUpdated : public Event {
public:
    ExerciseUpdated(const std::string& exerciseId,
                    const std::string& userId,
                    const std::vector<std::string>& updatedFields,
                    const std::string& name)
        : Event("ExerciseUpdated", exerciseId, "Exercise")
        , exerciseId_(exerciseId)
        , userId_(userId)
        , updatedFields_(updatedFields)
        , name_(name)
    {}

    Poco::JSON::Object::Ptr payload() const override {
        Poco::JSON::Object::Ptr p = new Poco::JSON::Object;
        p->set("exercise_id", exerciseId_);
        p->set("user_id", userId_);
        Poco::JSON::Array::Ptr fields = new Poco::JSON::Array;
        for (const auto& f : updatedFields_) {
            fields->add(f);
        }
        p->set("updated_fields", fields);
        p->set("name", name_);
        p->set("updated_at", static_cast<double>(Poco::Timestamp().epochMicroseconds()) / 1000);
        return p;
    }

private:
    std::string exerciseId_, userId_, name_;
    std::vector<std::string> updatedFields_;
};

class WorkoutCreated : public Event {
public:
    WorkoutCreated(const std::string& workoutId,
                   const std::string& userId,
                   const std::string& name,
                   const std::string& date)
        : Event("WorkoutCreated", workoutId, "Workout")
        , workoutId_(workoutId)
        , userId_(userId)
        , name_(name)
        , date_(date)
    {}

    Poco::JSON::Object::Ptr payload() const override {
        Poco::JSON::Object::Ptr p = new Poco::JSON::Object;
        p->set("workout_id", workoutId_);
        p->set("user_id", userId_);
        p->set("name", name_);
        p->set("date", date_);
        return p;
    }

private:
    std::string workoutId_, userId_, name_, date_;
};

class ExerciseAddedToWorkout : public Event {
public:
    ExerciseAddedToWorkout(const std::string& workoutId,
                           const std::string& exerciseId,
                           const std::string& userId,
                           int sets,
                           int reps)
        : Event("ExerciseAddedToWorkout", workoutId, "Workout")
        , workoutId_(workoutId)
        , exerciseId_(exerciseId)
        , userId_(userId)
        , sets_(sets)
        , reps_(reps)
    {}

    Poco::JSON::Object::Ptr payload() const override {
        Poco::JSON::Object::Ptr p = new Poco::JSON::Object;
        p->set("workout_id", workoutId_);
        p->set("exercise_id", exerciseId_);
        p->set("user_id", userId_);
        p->set("sets", sets_);
        p->set("reps", reps_);
        p->set("added_at", static_cast<double>(Poco::Timestamp().epochMicroseconds()) / 1000);
        return p;
    }

private:
    std::string workoutId_, exerciseId_, userId_;
    int sets_, reps_;
};

}  // namespace Events
}  // namespace FitnessTracker
