#!/Users/rlm/Desktop/Code/vibe-code-benchmark/.venv/bin/python

from mcp.server.fastmcp import FastMCP
# Create an MCP server
mcp = FastMCP("perry")

# Add a tool to query info about Perry
@mcp.tool()
def perry():
    """
    Query the info about Perry
    """
    return {
        "name": "Perry",
        "age": 99,
        "gender": "male",
        "location": "New York",
        "occupation": "Software Engineer",
        "interests": ["reading", "traveling", "cooking"],
        "favorite_color": "blue",
        "favorite_food": "pizza",
        "favorite_movie": "The Dark Knight",
        "favorite_music": "The Beatles",
        "favorite_sport": "basketball",
        "favorite_hobby": "reading",
        "favorite_activity": "traveling",
        "favorite_activity": "cooking",
    }



if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
