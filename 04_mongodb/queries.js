// Примеры запросов. mongosh fitness_tracker < queries.js

db = db.getSiblingDB("fitness_tracker");

print("1) ФИО по подстроке");
db.users
  .find(
    {
      $expr: {
        $regexMatch: {
          input: { $concat: ["$first_name", " ", "$last_name"] },
          regex: "ова",
          options: "i",
        },
      },
    },
    { login: 1, first_name: 1, last_name: 1, _id: 0 },
  )
  .forEach(printjson);

print("2) Упражнения, в названии «жим»");
db.exercises
  .find({ name: { $regex: "жим", $options: "i" } }, { name: 1, _id: 0 })
  .forEach(printjson);

print("3) Число тренировок по user_id");
db.workouts
  .aggregate([{ $group: { _id: "$user_id", cnt: { $sum: 1 } } }, { $sort: { cnt: -1 } }, { $limit: 5 }])
  .forEach(printjson);

print("4) Слотов упражнений за март 2025");
db.workouts
  .aggregate([
    { $match: { workout_date: { $gte: "2025-03-01", $lte: "2025-03-31" } } },
    { $project: { user_id: 1, n: { $size: { $ifNull: ["$items", []] } } } },
    { $group: { _id: "$user_id", exercises_slots: { $sum: "$n" } } },
    { $sort: { exercises_slots: -1 } },
  ])
  .forEach(printjson);

print("5) Длина названия тренировки");
db.workouts
  .aggregate([{ $project: { _id: 0, name: 1, len: { $strLenCP: "$name" } } }, { $limit: 5 }])
  .forEach(printjson);

print("6) Тренировки без упражнений");
db.workouts.find({ items: { $size: 0 } }, { _id: 1, user_id: 1, name: 1 }).forEach(printjson);
