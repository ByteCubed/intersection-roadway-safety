FROM adoptopenjdk/openjdk11 AS build

WORKDIR /usr/src/app

COPY gradle gradle
COPY gradlew .
COPY settings.gradle .
COPY build.gradle .
COPY src src

RUN ./gradlew --no-daemon build


FROM adoptopenjdk/openjdk11

WORKDIR /usr/src/app
COPY --from=build /usr/src/app/build/libs/*.jar .

CMD [ "java", "-jar", "dot-road-safety-0.0.1-SNAPSHOT.jar" ]
