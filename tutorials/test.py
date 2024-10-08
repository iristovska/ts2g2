import os
import sys
nb_dir = os.path.split(os.getcwd())[0]
if nb_dir not in sys.path:
    sys.path.append(nb_dir)

from core.model import Timeseries, TimeseriesPreprocessing, TimeseriesPreprocessingSegmentation, TimeseriesPreprocessingSlidingWindow, TimeseriesPreprocessingComposite, TimeseriesView, TimeGraph, ToSequenceVisitorSlidingWindow, ToSequenceVisitor

from tsg_io.input import CsvFile
from from_graph.strategy_to_time_sequence import StrategyNextValueInNodeRandom, StrategyNextValueInNodeRandomForSlidingWindow, StrategyNextValueInNodeRoundRobin, StrategyNextValueInNodeRoundRobinForSlidingWindow, StrategySelectNextNodeRandomlyFromNeighboursAcrossGraphs, StrategySelectNextNodeRandomlyFromNeighboursFromFirstGraph, StrategySelectNextNodeRandomly, StrategySelectNextNodeRandomDegree, StrategySelectNextNodeRandomWithRestart
from to_graph.strategy_linking_graph import StrategyLinkingGraphByValueWithinRange, LinkNodesWithinGraph
from to_graph.strategy_linking_multi_graphs import LinkGraphs
from to_graph.strategy_to_graph import BuildTimeseriesToGraphNaturalVisibilityStrategy, BuildTimeseriesToGraphHorizontalVisibilityStrategy

amazon_path = os.path.join(os.getcwd(), "amazon", "AMZN.csv")
apple_path = os.path.join(os.getcwd(), "apple", "APPLE.csv")



timegraph_1 = Timeseries(CsvFile(amazon_path, "Close").from_csv())\
    .with_preprocessing(TimeseriesPreprocessingSegmentation(60, 90))\
    .to_graph(BuildTimeseriesToGraphNaturalVisibilityStrategy().with_limit(1).get_strategy())\
    .add_edge(0,2)\
    .add_edge(13, 21, weight = 17)\
    .link(LinkNodesWithinGraph().by_value(StrategyLinkingGraphByValueWithinRange(2)).seasonalities(15))\
    .draw("blue")

timegraph_2 = Timeseries(CsvFile(apple_path, "Close").from_csv())\
    .with_preprocessing(TimeseriesPreprocessingComposite()\
        .add(TimeseriesPreprocessingSegmentation(60, 120))\
        .add(TimeseriesPreprocessingSlidingWindow(5)))\
    .to_graph(BuildTimeseriesToGraphNaturalVisibilityStrategy().get_strategy())\
    .link(LinkGraphs().sliding_window())\
    .combine_identical_subgraphs()\
    .draw("red")

timegraph_3 = Timeseries(CsvFile(apple_path, "Close").from_csv())\
    .with_preprocessing(TimeseriesPreprocessingSegmentation(60, 90))\
    .add(Timeseries(CsvFile(apple_path, "Close").from_csv())\
        .with_preprocessing(TimeseriesPreprocessingSegmentation(90, 120)))\
    .add(Timeseries(CsvFile(apple_path, "Close").from_csv())\
        .with_preprocessing(TimeseriesPreprocessingSegmentation(150, 180)))\
    .to_graph(BuildTimeseriesToGraphNaturalVisibilityStrategy().with_limit(1).get_strategy())\
    .link(LinkGraphs().time_cooccurrence())\
    .link(LinkNodesWithinGraph().by_value(StrategyLinkingGraphByValueWithinRange(0.5)))\
    .combine_identical_nodes()\
    .draw("brown")

timegraph_4 = Timeseries(CsvFile(apple_path, "Close").from_csv())\
    .with_preprocessing(TimeseriesPreprocessingComposite()\
        .add(TimeseriesPreprocessingSegmentation(60, 110))\
        .add(TimeseriesPreprocessingSlidingWindow(5)))\
    .add(Timeseries(CsvFile(apple_path, "Close").from_csv())\
        .with_preprocessing(TimeseriesPreprocessingComposite()\
            .add(TimeseriesPreprocessingSegmentation(120, 170))\
            .add(TimeseriesPreprocessingSlidingWindow(5)))\
        .add(Timeseries(CsvFile(apple_path, "Close").from_csv())\
            .with_preprocessing(TimeseriesPreprocessingComposite()\
                    .add(TimeseriesPreprocessingSegmentation(190, 240))\
                    .add(TimeseriesPreprocessingSlidingWindow(5)))))\
    .to_graph(BuildTimeseriesToGraphNaturalVisibilityStrategy().get_strategy())\
    .link(LinkGraphs().sliding_window().time_cooccurrence())\
    .combine_identical_subgraphs()\
    .link(LinkNodesWithinGraph().seasonalities(15))\
    .draw("green")


timegraph_1.to_sequence(ToSequenceVisitor()\
        .next_node_strategy(StrategySelectNextNodeRandomWithRestart())\
        .next_value_strategy(StrategyNextValueInNodeRoundRobin().skip_every_x_steps(1))\
        .ts_length(100))\
    .draw_sequence()


timegraph_2.to_sequence(ToSequenceVisitorSlidingWindow()\
    .next_node_strategy(StrategySelectNextNodeRandomly())\
    .next_value_strategy(StrategyNextValueInNodeRandomForSlidingWindow().skip_every_x_steps(1))\
    .ts_length(50))\
    .draw_sequence()


timegraph_3.to_sequence(ToSequenceVisitor()\
    .next_node_strategy(StrategySelectNextNodeRandomlyFromNeighboursAcrossGraphs().change_graphs_every_x_steps(2))\
    .next_value_strategy(StrategyNextValueInNodeRoundRobin().skip_every_x_steps(1))\
    .ts_length(50))\
    .draw_sequence()


timegraph_4.to_sequence(ToSequenceVisitorSlidingWindow()\
    .next_node_strategy(StrategySelectNextNodeRandomlyFromNeighboursAcrossGraphs())\
    .next_value_strategy(StrategyNextValueInNodeRoundRobinForSlidingWindow())\
    .ts_length(100))\
    .draw_sequence()
