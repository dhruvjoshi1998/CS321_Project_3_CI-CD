from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect
from flask.wrappers import Response

app = Flask(__name__)

archived = []

days_of_week = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
todo_list = [[] for _ in range(len(days_of_week))]
day_to_idx = {day: i for i, day in enumerate(days_of_week)}


@app.route("/")
def home():

    enumerated_todo_list = [enumerate(day) for day in todo_list]
    print(archived)
    return render_template(
        "base.html",
        enumerated_todo_list=zip(
            [*range(len(days_of_week))], days_of_week, enumerated_todo_list
        ),
        archived=archived,
    )


@app.route("/time_feed/")
def time_feed():
    def generate_time():
        yield datetime.now().strftime("%H:%M:%S")

    return Response(generate_time(), mimetype="text")


@app.route("/add/", methods=["POST"])
def add():
    new_todo_item = request.form.get("new_todo")
    priority = request.form.get("priority")
    dow = request.form.get("dow")
    tags = request.form.get("tags").split(" ")
    new_tags = []
    for t in tags:
        new_tags.append("#" + t)
    time = datetime.now().strftime("%H:%M")

    todo_list[day_to_idx[dow]].append(
        (
            new_todo_item,
            {"check": 0, "priority": priority, "tags": new_tags, "time": time},
        )
    )

    return redirect(url_for("home"))


@app.route("/remove/<int:day_number>/<int:task_number>")
def remove(day_number, task_number):
    todo_list[day_number].pop(task_number)
    return redirect(url_for("home"))


@app.route("/clear")
def clear_completed():
    remove = []
    for i, day in enumerate(todo_list):
        for j, (task_name, data) in enumerate(day):
            if data["check"]:
                archived.append(day[j])
                remove.append((i, j))

    for i, j in reversed(remove):
        todo_list[i].pop(j)

    return redirect(url_for("home"))


@app.route("/up/<int:day_number>/<int:task_number>")
def up(day_number, task_number):
    if task_number != 0:
        todo_list[day_number][task_number - 1], todo_list[day_number][task_number] = (
            todo_list[day_number][task_number],
            todo_list[day_number][task_number - 1],
        )

    return redirect(url_for("home"))


@app.route("/down/<int:day_number>/<int:task_number>")
def down(day_number, task_number):
    if task_number != len(todo_list[day_number]) - 1:
        todo_list[day_number][task_number], todo_list[day_number][task_number + 1] = (
            todo_list[day_number][task_number + 1],
            todo_list[day_number][task_number],
        )

    return redirect(url_for("home"))


@app.route("/toggle_check/<int:day_number>/<int:task_number>")
def toggle_check(day_number, task_number):
    todo_list[day_number][task_number][1]["check"] = (
        0 if todo_list[day_number][task_number][1]["check"] else 1
    )

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run()
