from fire import Fire
import jinja2 as j2
from chainfury import programatic_actions_registry, ai_actions_registry, memory_registry, model_registry


def main(src_file: str, trg_file: str, v: bool = False):
    with open(src_file, "r") as f:
        temp = j2.Template(f.read())

    pc = [
        {
            "id": node.id,
            "description": node.description.rstrip(".")
            + f'. Copy: ``programatic_actions_registry.get("{node.id}")``',
        }
        for node_id, node in programatic_actions_registry.nodes.items()
    ]
    ac = [
        {
            "id": node.id,
            "description": node.description.rstrip(".")
            + f'. Copy: ``ai_actions_registry.get("{node.id}")``',
        }
        for node_id, node in ai_actions_registry.nodes.items()
    ]
    mc = []
    for node_id, node in memory_registry._memories.items():
        fn = "get_read" if node.id.endswith("-read") else "get_write"
        mc.append(
            {
                "id": node.id,
                "description": node.description.rstrip(".") + f'. Copy: ``memory_registry.{fn}("{node.id}")``',
            }
        )

    moc = [
        {
            "id": model_id,
            "description": model.description.rstrip(".")
            + f'. Copy: ``model_registry.get("{model_id}")``',
        }
        for model_id, model in model_registry.models.items()
    ]
    op = temp.render(pc=pc, ac=ac, mc=mc, moc=moc)
    if v:
        print(op)
        print("Writing to", trg_file)

    with open(trg_file, "w") as f:
        f.write(op)


if __name__ == "__main__":
    Fire(main)
