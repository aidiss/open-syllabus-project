

import math
import os
import pgmagick as pgm

from osp.graphs.graph import Graph

from cached_property import cached_property
from clint.textui import progress


class Gephi_Graph(Graph):


    def xs(self):

        """
        Yields: The next X-axis coordinate.
        """

        for cn, node in self.graph.nodes_iter(data=True):
            yield node['x']


    def ys(self):

        """
        Yields: The next Y-axis coordinate.
        """

        for cn, node in self.graph.nodes_iter(data=True):
            yield node['y']


    @cached_property
    def min_x(self):

        """
        Returns: The minimum X-axis coordinate.
        """

        return min(list(self.xs()))


    @cached_property
    def max_x(self):

        """
        Returns: The maximum X-axis coordinate.
        """

        return max(list(self.xs()))


    @cached_property
    def min_y(self):

        """
        Returns: The minimum Y-axis coordinate.
        """

        return min(list(self.ys()))


    @cached_property
    def max_y(self):

        """
        Returns: The maximum Y-axis coordinate.
        """

        return max(list(self.ys()))


    @cached_property
    def height(self):

        """
        Returns: The Y-axis coordinate range.
        """

        return math.ceil(self.max_y - self.min_y)


    @cached_property
    def width(self):

        """
        Returns: The X-axis coordinate range.
        """

        return math.ceil(self.max_x - self.min_x)


    def render(self, out_path, size=10000, scale=5, bg_color='#003059'):

        """
        Render a PNG.
        """

        image = pgm.Image(
            pgm.Geometry(size, size),
            pgm.Color(bg_color),
        )

        # TODO: font

        nodes = self.graph.nodes_iter(data=True)
        count = len(self.graph)

        for tid, n in progress.bar(nodes, expected_size=count):

            # Get X/Y, radius.
            x =  (n['x']*scale) + (size/2)
            y = -(n['y']*scale) + (size/2)
            r =  (n['size']*scale) / 2

            # Index the coordinates.
            self.graph.node[tid]['pixel_x'] = x
            self.graph.node[tid]['pixel_y'] = y
            self.graph.node[tid]['pixel_r'] = r

            # ** Node **

            # Hex-ify color.
            color = '#%02x%02x%02x' % (
                n['r'],
                n['g'],
                n['b']
            )

            # Draw the node.
            node = pgm.DrawableList()
            node.append(pgm.DrawableFillColor(color))
            node.append(pgm.DrawableStrokeColor('black'))
            node.append(pgm.DrawableStrokeWidth(r/15))
            node.append(pgm.DrawableStrokeOpacity(0.9))
            node.append(pgm.DrawableCircle(x, y, x+r, y+r))
            image.draw(node)

            # ** Label **

            label = ', '.join(n['title'], n['author'])

            # TODO|dev
            image.fontPointsize(n['size'])

            # Measure the width of the label.
            tm = pgm.TypeMetric()
            image.fontTypeMetrics(label, tm)
            tw = tm.textWidth()

            # Draw the label.
            label = pgm.DrawableList()
            label.append(pgm.DrawablePointSize(n['size']))
            label.append(pgm.DrawableFillColor('white'))
            label.append(pgm.DrawableText(x-(tw/2), y, label))
            image.draw(label)

        image.write(os.path.abspath(out_path))
