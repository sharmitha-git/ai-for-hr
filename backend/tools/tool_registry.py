
TOOLS = {}


def register_tool(name):

    def decorator(func):

        TOOLS[name] = func

        return func

    return decorator


def execute_tool(
    tool_name,
    **kwargs
):

    tool = TOOLS.get(tool_name)

    if not tool:

        raise Exception(
            f"Tool not found: {tool_name}"
        )

    return tool(**kwargs)


