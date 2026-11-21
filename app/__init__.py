"""The document intelligence service, in hexagonal shape (Part III).

app/ports.py      what the core needs from the outside world
app/core/         the decisions: policies, handlers — imports ports only
app/adapters/     every concrete technology
app/composition.py  the only place that wires adapters to ports (3.4)
"""
