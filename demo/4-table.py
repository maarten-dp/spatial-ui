import os.path as osp

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

from spatial_ui.window import App, GLFWWindow
from spatial_ui.elements import Panel, Table
from spatial_ui.data_connection.sqla import SQLADataReader
from spatial_ui.layout.css import CSSLayout

import sys
import glfw
from arcade_curtains.animation import interp2d

Base = declarative_base()


def get_session():
    engine = create_engine("sqlite:///")
    with Session(engine) as session:
        Base.metadata.create_all(engine)
        yield session


class Adiminimini(Base):
    __tablename__ = 'adiminimini'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))


class AutoGLFWWindow(GLFWWindow):
    def __init__(self, start_at, speed, points, repeat=1, *args, **kwargs):
        points *= repeat
        speed = [(start_at + (speed * i)) for i in range(len(points))]

        super().__init__(*args, **kwargs)
        self.speed = speed[-1]
        self.point_factory = interp2d(speed, points)
        self.hover_handler = None

    def set_hover_handler(self, handler):
        self.hover_handler = handler

    def mouse_position(self):
        time = glfw.get_time()
        print(time)
        if time > self.speed:
            sys.exit(0)

        try:
            x, y = self.point_factory(time)
        except ValueError:
            return (0, 0)
        pos = (int(x), int(y))
        print(pos)
        self.hover_handler(None, *pos)


session = next(get_session())
session.add(Adiminimini(first_name="Eric", last_name="Gazoni"))
session.add(Adiminimini(first_name="Maarten", last_name="De Paepe"))
session.add(Adiminimini(first_name="Jens", last_name="Roelant"))
session.add(Adiminimini(first_name="Bram", last_name="Vereertbrugghen"))
session.add(Adiminimini(first_name="Kenny", last_name="Van de Maele"))
session.add(Adiminimini(first_name="Pierre", last_name="Savatte"))
session.add(Adiminimini(first_name="Jean", last_name="Nassar"))
session.add(Adiminimini(first_name="Aurélie", last_name="Pradeau"))
session.add(Adiminimini(first_name="Benjamin", last_name="Grandhomme"))
session.add(Adiminimini(first_name="Hans", last_name="Degroote"))
session.add(Adiminimini(first_name="Ann", last_name="Peeters"))
session.commit()

points = [
    (50, 50),
    (250, 50),
    (250, 250),
    (50, 250),
]

css_file = osp.join(osp.abspath(osp.dirname(__file__)), "4-table.css")
layout = CSSLayout.from_filepath(css_file, observe=True)
window = App(
    width=500,
    height=500,
    layout=layout,
    window=AutoGLFWWindow(
        start_at=0.6,
        speed=0.1,
        points=points,
        repeat=1,
        width=500,
        height=500
    )
)

data_connection = SQLADataReader(session, Adiminimini, show_index=False)
panel = Panel(
    Table(data_connection=data_connection),
)

layout.set_element_tree(panel)
window.run_forever()