cmake_minimum_required(VERSION 3.16)
project(fitness_tracker_events VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

find_package(Poco REQUIRED COMPONENTS Foundation JSON Util)
find_package(PkgConfig REQUIRED)
pkg_check_modules(RDKAFKA REQUIRED IMPORTED_TARGET rdkafka)
pkg_check_modules(RDKAFKACPP REQUIRED IMPORTED_TARGET rdkafka++)

add_library(events
    src/events/kafka_producer.cpp
    src/events/kafka_consumer.cpp
)

target_include_directories(events PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/includes
    ${Poco_INCLUDE_DIRS}
)

target_link_libraries(events PUBLIC
    ${Poco_LIBRARIES}
    PkgConfig::RDKAFKA
    PkgConfig::RDKAFKACPP
)

add_executable(fitness_events_demo
    src/demo/main.cpp
)

target_include_directories(fitness_events_demo PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/includes
    ${Poco_INCLUDE_DIRS}
)

target_link_libraries(fitness_events_demo PRIVATE events)

install(TARGETS fitness_events_demo DESTINATION bin)
