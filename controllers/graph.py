from kivy.config import Config
Config.set('kivy', 'log_enable', 0)
Config.set('kivy', 'log_level', 'critical')

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.garden.graph import Graph, MeshLinePlot
from kivy.clock import mainthread


def reset_window():
    import kivy.core.window as window
    from kivy.base import EventLoop

    if not EventLoop.event_listeners:
        from kivy.cache import Cache
        window.Window = window.core_select_lib(
            'window',
            window.window_impl,
            True,
        )

        for cat in Cache._categories:
            Cache._objects[cat] = {}



class FunGraphApp(App):
    """Kivy class to draw funcs."""
    graph = ObjectProperty(allownone=True)

    def build(self):
        self.graph = Graph()
        return self.graph

    @mainthread
    def create_curve(self, formula, kwargs):
        graph = self.graph

        graph.xlabel='X'
        graph.ylabel='Y'
        graph.x_ticks_minor=5
        graph.y_grid_label=True
        graph.x_grid_label=True
        graph.padding=5
        graph.x_grid=True
        graph.y_grid=True
        graph.background_color = [.95, .95, .95, 1]
        graph.border_color = [0, 0, 0, 1]
        graph.tick_color = [.6, .6, .6, 1]
        graph.label_options = {'color': [.2, .2, .2, 1]}

        graph.xmin = kwargs.get('xmin', -50)
        graph.xmax = kwargs.get('xmax', 50)
        graph.ymin = kwargs.get('ymin', -50)
        graph.ymax = kwargs.get('ymax', 50)

        dx = graph.xmax -  graph.xmin
        dy = graph.ymax -  graph.ymin

        graph.x_ticks_major = int(dx / 10)
        graph.y_ticks_major = int(dy / 10)

        plot = MeshLinePlot(color=[1, 0, 0, 1])
        f_range = repr((int(graph.xmin), int(graph.xmin + dx)))
        points = eval(formula % f_range)
        plot.points = points
        self.graph.add_plot(plot)
