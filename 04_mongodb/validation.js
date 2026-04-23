// ДЗ 04. mongosh fitness_tracker < validation.js

db = db.getSiblingDB("fitness_tracker");

["workouts", "exercises", "users"].forEach((name) => {
  if (db.getCollectionNames().includes(name)) {
    db.getCollection(name).drop();
  }
});

const uuid =
  "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$";

db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "_id",
        "login",
        "password_hash",
        "first_name",
        "last_name",
        "created_at",
        "updated_at",
      ],
      properties: {
        _id: { bsonType: "string", pattern: uuid },
        login: { bsonType: "string", minLength: 1, maxLength: 100 },
        password_hash: { bsonType: "string", minLength: 64, maxLength: 64 },
        first_name: { bsonType: "string", minLength: 1, maxLength: 100 },
        last_name: { bsonType: "string", minLength: 1, maxLength: 100 },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" },
      },
    },
  },
  validationLevel: "strict",
  validationAction: "error",
});

db.createCollection("exercises", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "name", "created_at"],
      properties: {
        _id: { bsonType: "string", pattern: uuid },
        name: { bsonType: "string", minLength: 1, maxLength: 200 },
        description: { bsonType: ["string", "null"] },
        created_at: { bsonType: "date" },
      },
    },
  },
  validationLevel: "strict",
  validationAction: "error",
});

db.createCollection("workouts", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "user_id", "name", "workout_date", "items", "created_at"],
      properties: {
        _id: { bsonType: "string", pattern: uuid },
        user_id: { bsonType: "string", pattern: uuid },
        name: { bsonType: "string", minLength: 1, maxLength: 200 },
        workout_date: {
          bsonType: "string",
          pattern: "^\\d{4}-\\d{2}-\\d{2}$",
        },
        items: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["exercise_id", "position"],
            properties: {
              exercise_id: { bsonType: "string", pattern: uuid },
              position: { bsonType: "int", minimum: 0 },
            },
          },
        },
        created_at: { bsonType: "date" },
      },
    },
  },
  validationLevel: "strict",
  validationAction: "error",
});

db.users.createIndex({ login: 1 }, { unique: true });
db.exercises.createIndex({ name: 1 });
db.workouts.createIndex({ user_id: 1, workout_date: -1 });

try {
  db.users.insertOne({
    _id: "not-a-uuid",
    login: "bad",
    password_hash: "0".repeat(64),
    first_name: "X",
    last_name: "Y",
    created_at: new Date(),
    updated_at: new Date(),
  });
  print("FAIL: validator");
} catch (e) {
  print("OK: invalid doc rejected");
}
