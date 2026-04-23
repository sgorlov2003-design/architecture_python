// После validation.js

db = db.getSiblingDB("fitness_tracker");

const now = new Date();
const pass = "9b8769a4a742959a2d0298c36fb70623f2dfacda8436237df08d8dfd5b37374c";

const U = [
  "233d9afd-a0be-48d3-a45a-9c2a0565d5a0",
  "89547951-016b-4898-8bf7-9c976cafa40b",
  "a33e30f5-55d5-4d5a-ade4-5135ade2ed86",
  "ba379253-7312-4da1-a24e-7901e0f8fb07",
  "a3eacf65-654d-48a4-92b5-e040a550f19d",
  "a7255caf-c31f-4f9b-93df-d53ac539233e",
  "db1c6cdc-bb69-49ac-b0c5-50421296bf6f",
  "df0beabc-566e-4614-963f-b8749d65f6d3",
  "17ea5b84-fc1e-4909-9c27-ff0a81aff56a",
  "fdc49d3e-3587-4b8d-82db-754a19f7fc90",
  "9eaef543-a24e-486a-9459-3327cd246163",
  "5b142a04-a813-4370-bac3-5547815bccbc",
];

const E = [
  "c77bfe82-7379-45eb-aa6e-7825283a39dc",
  "5b07db3b-c14c-48d5-bbd5-ab53e822743d",
  "d07e0c60-d156-4290-8e15-d63e91ebf3a5",
  "276ada70-e04d-4766-a2bc-bbd883aae1d2",
  "ce6a6086-2ba7-4a2b-a004-d6880f0e8f42",
  "50840051-3c6a-46ff-98bf-7d43e690d22b",
  "8f9a1218-1c84-4359-aeea-8c5842779944",
  "a072ecf8-891d-4986-b253-efe0f1c68843",
  "a943f689-f865-4b0e-bb83-b871a1db7433",
  "cf709f54-9f81-4b41-b802-6c79c519bed8",
  "7ba84eb2-51a8-49b1-9d02-3dc4b10f275d",
  "ea451194-f4d1-4784-ab53-4067f416209a",
  "3f9950f3-81a0-4c7f-981a-3fcb1d8d548c",
  "f147b636-5fb2-4530-a60f-23ef8dca2c48",
  "3d51ad70-eaa5-4adc-b6d7-27b4f74135bc",
];

const W = [
  "0afd5a72-11dd-486b-a669-a2c5c64bd3de",
  "3b3d9fe2-433f-416b-9df2-04793b11bf97",
  "d278fb46-ad79-40ff-b55d-8dabe0d1dcc6",
  "95d429bb-d364-4156-9b2b-3d15fa02901e",
  "4ca7efaa-5aad-4fea-b94d-70f6683240f5",
  "cd4e16f0-cdce-4de2-b0da-058f90f50d81",
  "5596dc07-c1bc-4d81-8fc7-efd1f716c943",
  "32173354-047a-4084-8a8c-6b27a71f946b",
  "665f54a3-c10e-4afc-a4bb-f45f0ab7aa84",
  "b700f2be-6693-40e6-9e1e-173092393fba",
  "29ef1627-3d80-4fcf-927b-d1ae8daee626",
  "7b9eb377-b45b-4abf-99ee-c0be9cfb4943",
];

db.users.insertMany([
  { _id: U[0], login: "ivan_p", password_hash: pass, first_name: "Иван", last_name: "Петров", created_at: now, updated_at: now },
  { _id: U[1], login: "maria_s", password_hash: pass, first_name: "Мария", last_name: "Сидорова", created_at: now, updated_at: now },
  { _id: U[2], login: "alex_k", password_hash: pass, first_name: "Алексей", last_name: "Козлов", created_at: now, updated_at: now },
  { _id: U[3], login: "olga_m", password_hash: pass, first_name: "Ольга", last_name: "Морозова", created_at: now, updated_at: now },
  { _id: U[4], login: "dmitry_v", password_hash: pass, first_name: "Дмитрий", last_name: "Волков", created_at: now, updated_at: now },
  { _id: U[5], login: "elena_n", password_hash: pass, first_name: "Елена", last_name: "Новикова", created_at: now, updated_at: now },
  { _id: U[6], login: "sergey_l", password_hash: pass, first_name: "Сергей", last_name: "Лебедев", created_at: now, updated_at: now },
  { _id: U[7], login: "anna_r", password_hash: pass, first_name: "Анна", last_name: "Романова", created_at: now, updated_at: now },
  { _id: U[8], login: "pavel_t", password_hash: pass, first_name: "Павел", last_name: "Тихонов", created_at: now, updated_at: now },
  { _id: U[9], login: "natalia_f", password_hash: pass, first_name: "Наталья", last_name: "Фёдорова", created_at: now, updated_at: now },
  { _id: U[10], login: "igor_b", password_hash: pass, first_name: "Игорь", last_name: "Белов", created_at: now, updated_at: now },
  { _id: U[11], login: "ksenia_g", password_hash: pass, first_name: "Ксения", last_name: "Громова", created_at: now, updated_at: now },
]);

db.exercises.insertMany([
  { _id: E[0], name: "Приседания со штангой", description: "Базовое движение для ног", created_at: now },
  { _id: E[1], name: "Становая тяга", description: "Задняя поверхность бедра и спина", created_at: now },
  { _id: E[2], name: "Жим штанги лёжа", description: "Грудные и трицепсы", created_at: now },
  { _id: E[3], name: "Подтягивания", description: "Верх спины", created_at: now },
  { _id: E[4], name: "Отжимания", description: "Без оборудования", created_at: now },
  { _id: E[5], name: "Планка", description: "Корпус, статика", created_at: now },
  { _id: E[6], name: "Выпады", description: "Ноги, координация", created_at: now },
  { _id: E[7], name: "Тяга верхнего блока", description: "Широчайшие", created_at: now },
  { _id: E[8], name: "Жим гантелей стоя", description: "Плечи", created_at: now },
  { _id: E[9], name: "Скручивания", description: "Пресс", created_at: now },
  { _id: E[10], name: "Бёрпи", description: "Кардио и всё тело", created_at: now },
  { _id: E[11], name: "Гиперэкстензия", description: "Поясница", created_at: now },
  { _id: E[12], name: "Подъём на икры", description: "Икры", created_at: now },
  { _id: E[13], name: "Французский жим", description: "Трицепс", created_at: now },
  { _id: E[14], name: "Сгибания на бицепс", description: "Руки", created_at: now },
]);

db.workouts.insertMany([
  { _id: W[0], user_id: U[0], name: "Ноги", workout_date: "2025-03-10", items: [{ exercise_id: E[0], position: 0 }, { exercise_id: E[6], position: 1 }], created_at: now },
  { _id: W[1], user_id: U[0], name: "Верх тела", workout_date: "2025-03-12", items: [{ exercise_id: E[2], position: 0 }, { exercise_id: E[7], position: 1 }], created_at: now },
  { _id: W[2], user_id: U[1], name: "Утро дома", workout_date: "2025-03-11", items: [{ exercise_id: E[4], position: 0 }, { exercise_id: E[5], position: 1 }], created_at: now },
  { _id: W[3], user_id: U[2], name: "Спина", workout_date: "2025-03-09", items: [{ exercise_id: E[1], position: 0 }, { exercise_id: E[3], position: 1 }], created_at: now },
  { _id: W[4], user_id: U[2], name: "Кардио", workout_date: "2025-03-13", items: [{ exercise_id: E[10], position: 0 }], created_at: now },
  { _id: W[5], user_id: U[3], name: "Пресс и кор", workout_date: "2025-03-08", items: [{ exercise_id: E[5], position: 0 }, { exercise_id: E[9], position: 1 }], created_at: now },
  { _id: W[6], user_id: U[4], name: "Плечи", workout_date: "2025-03-14", items: [{ exercise_id: E[8], position: 0 }], created_at: now },
  { _id: W[7], user_id: U[5], name: "Руки", workout_date: "2025-03-07", items: [{ exercise_id: E[13], position: 0 }, { exercise_id: E[14], position: 1 }], created_at: now },
  { _id: W[8], user_id: U[6], name: "Низ спины", workout_date: "2025-03-06", items: [{ exercise_id: E[11], position: 0 }], created_at: now },
  { _id: W[9], user_id: U[7], name: "Икры и ноги", workout_date: "2025-03-15", items: [{ exercise_id: E[12], position: 0 }, { exercise_id: E[0], position: 1 }], created_at: now },
  { _id: W[10], user_id: U[8], name: "Смешанная", workout_date: "2025-03-05", items: [{ exercise_id: E[2], position: 0 }, { exercise_id: E[4], position: 1 }, { exercise_id: E[5], position: 2 }], created_at: now },
  { _id: W[11], user_id: U[9], name: "Лёгкая", workout_date: "2025-03-16", items: [], created_at: now },
]);

printjson({
  users: db.users.countDocuments({}),
  exercises: db.exercises.countDocuments({}),
  workouts: db.workouts.countDocuments({}),
});
