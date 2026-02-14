from __future__ import annotations

from langgraph.graph import StateGraph, END

from app.models.state import PipelineState
from app.graph.nodes.ingest import ingest_node
from app.graph.nodes.analyze import analyze_node
from app.graph.nodes.crossref import crossref_node
from app.graph.nodes.venue import venue_node
from app.graph.nodes.coach import coach_node
from app.graph.edges import should_include_venue


def build_graph() -> StateGraph:
    graph = StateGraph(PipelineState)

    graph.add_node("ingest", ingest_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("crossref", crossref_node)
    graph.add_node("venue", venue_node)
    graph.add_node("coach", coach_node)

    graph.set_entry_point("ingest")
    graph.add_edge("ingest", "analyze")
    graph.add_edge("analyze", "crossref")
    graph.add_conditional_edges("crossref", should_include_venue, {"venue": "venue", "coach": "coach"})
    graph.add_edge("venue", "coach")
    graph.add_edge("coach", END)

    return graph.compile()
