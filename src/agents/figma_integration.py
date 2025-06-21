import requests
import json
import os
from typing import Dict, List
from agent_controller import AgentController

class FigmaParser:
    def __init__(self, access_token: str):
        """Initialize Figma parser with API token"""
        self.access_token = access_token
        self.base_url = "https://api.figma.com/v1"
        self.headers = {"X-Figma-Token": self.access_token}

    def get_file(self, file_key: str) -> Dict:
        """Fetch Figma file structure"""
        response = requests.get(
            f"{self.base_url}/files/{file_key}",
            headers=self.headers
        )
        return response.json()

    def extract_component(self, node_id: str, file_key: str) -> Dict:
        """Extract component details"""
        response = requests.get(
            f"{self.base_url}/files/{file_key}/nodes?ids={node_id}",
            headers=self.headers
        )
        return response.json()["nodes"][node_id]

    def convert_to_component_spec(self, figma_data: Dict) -> Dict:
        """Convert Figma data to component specification"""
        return {
            "name": figma_data["document"]["name"],
            "props": self._extract_props(figma_data["document"]),
            "styles": self._extract_styles(figma_data["document"]),
            "layout": self._extract_layout(figma_data["document"]),
            "content": self._extract_content(figma_data["document"])
        }

    def _extract_props(self, node: Dict) -> List[Dict]:
        """Identify component props from Figma properties"""
        props = []

        # Extract text content as potential props
        if "characters" in node:
            # If text contains data placeholders like {{name}}, extract as prop
            text = node.get("characters", "")
            import re
            prop_matches = re.findall(r'{{(\w+)}}', text)
            for match in prop_matches:
                props.append({
                    "name": match,
                    "type": "String"
                })

        # Extract layer names as potential props
        if "children" in node:
            for child in node["children"]:
                child_name = child.get("name", "")
                # If layer name starts with "prop:", extract as prop
                if child_name.startswith("prop:"):
                    prop_name = child_name.split(":")[1]
                    props.append({
                        "name": prop_name,
                        "type": "Any"
                    })
                # Recursively check child nodes
                child_props = self._extract_props(child)
                props.extend(child_props)

        return props

    def _extract_styles(self, node: Dict) -> Dict:
        """Convert Figma styles to Tailwind classes"""
        styles = {}

        # Extract colors
        if "fills" in node and node["fills"]:
            fill = node["fills"][0]
            if fill["type"] == "SOLID" and "color" in fill:
                styles["background"] = self._rgb_to_hex(fill["color"])

        # Extract typography
        if "style" in node:
            if "fontFamily" in node["style"]:
                styles["font"] = node["style"]["fontFamily"]
            if "fontSize" in node["style"]:
                styles["font_size"] = node["style"]["fontSize"]
            if "fontWeight" in node["style"]:
                styles["font_weight"] = node["style"]["fontWeight"]

        # Extract padding/margin
        if "absoluteBoundingBox" in node and "padding" in node:
            styles["padding"] = node["padding"]

        # Extract border radius
        if "cornerRadius" in node:
            styles["border_radius"] = node["cornerRadius"]

        # Convert to Tailwind classes
        tailwind_map = {
            "background": lambda x: f"bg-{self._nearest_tailwind_color(x)}",
            "font_size": lambda x: f"text-{self._map_font_size(x)}",
            "font_weight": lambda x: f"font-{self._map_font_weight(x)}",
            "border_radius": lambda x: f"rounded-{self._map_border_radius(x)}"
        }

        tailwind_classes = []
        for key, value in styles.items():
            if key in tailwind_map:
                tailwind_classes.append(tailwind_map[key](value))

        return " ".join(tailwind_classes)

    def _extract_layout(self, node: Dict) -> Dict:
        """Extract layout dimensions"""
        layout = {}

        if "absoluteBoundingBox" in node:
            box = node["absoluteBoundingBox"]
            layout["width"] = box.get("width")
            layout["height"] = box.get("height")

        # Detect layout type (flex, grid)
        if "layoutMode" in node:
            layout["type"] = node["layoutMode"]
            if node["layoutMode"] == "HORIZONTAL":
                layout["direction"] = "row"
            elif node["layoutMode"] == "VERTICAL":
                layout["direction"] = "column"

            # Spacing
            if "itemSpacing" in node:
                layout["spacing"] = node["itemSpacing"]

        return layout

    def _extract_content(self, node: Dict) -> str:
        """Extract text content"""
        if "characters" in node:
            return node["characters"]

        content = ""
        if "children" in node:
            for child in node["children"]:
                child_content = self._extract_content(child)
                if child_content:
                    content += child_content + "\n"

        return content.strip()

    def _rgb_to_hex(self, color: Dict) -> str:
        """Convert RGB to hex color"""
        r = int(color.get("r", 0) * 255)
        g = int(color.get("g", 0) * 255)
        b = int(color.get("b", 0) * 255)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _nearest_tailwind_color(self, hex_color: str) -> str:
        """Approximate hex to Tailwind color name"""
        # Simplified mapping - in practice use a color distance algorithm
        color_map = {
            "#ef4444": "red-500",
            "#ec4899": "pink-500",
            "#f97316": "orange-500",
            "#eab308": "yellow-500",
            "#22c55e": "green-500",
            "#3b82f6": "blue-500",
            "#8b5cf6": "violet-500",
            "#d1d5db": "gray-300",
            "#9ca3af": "gray-400",
            "#6b7280": "gray-500",
            "#4b5563": "gray-600",
            "#1f2937": "gray-800",
            "#111827": "gray-900",
            "#ffffff": "white",
            "#000000": "black"
        }
        # Default to gray-200 if no match
        return color_map.get(hex_color.lower(), "gray-200")

    def _map_font_size(self, size: float) -> str:
        """Map font size to Tailwind size"""
        if size <= 12:
            return "xs"
        elif size <= 14:
            return "sm"
        elif size <= 16:
            return "base"
        elif size <= 18:
            return "lg"
        elif size <= 20:
            return "xl"
        elif size <= 24:
            return "2xl"
        else:
            return "3xl"

    def _map_font_weight(self, weight: int) -> str:
        """Map font weight to Tailwind weight"""
        if weight < 400:
            return "light"
        elif weight < 500:
            return "normal"
        elif weight < 600:
            return "medium"
        elif weight < 700:
            return "semibold"
        else:
            return "bold"

    def _map_border_radius(self, radius: float) -> str:
        """Map border radius to Tailwind size"""
        if radius <= 2:
            return "sm"
        elif radius <= 4:
            return "md"
        elif radius <= 8:
            return "lg"
        elif radius <= 12:
            return "xl"
        else:
            return "2xl"

class FigmaToVueAgent:
    def __init__(self, figma_token: str):
        """Initialize Figma to Vue agent"""
        self.parser = FigmaParser(figma_token)
        self.agent = AgentController()

    async def generate_component(self, figma_url: str):
        """Generate Vue component from Figma URL"""
        # Extract file key and node ID from URL
        # Format: https://www.figma.com/file/FILE_KEY/...?node-id=NODE_ID
        try:
            file_key = figma_url.split("/file/")[1].split("/")[0]
            node_id = figma_url.split("node-id=")[1].split("&")[0]

            print(f"Extracting Figma data for file {file_key}, node {node_id}")

            # Fetch and parse Figma data
            figma_data = self.parser.extract_component(node_id, file_key)
            component_spec = self.parser.convert_to_component_spec(figma_data)

            # Generate Vue component
            await self.agent.generate_component(
                component_spec["name"],
                [prop["name"] for prop in component_spec["props"]]
            )

            # Add Tailwind styles
            tailwind_classes = component_spec["styles"]
            layout_info = self._convert_layout_to_tailwind(component_spec["layout"])

            # Update component with styles
            await self.agent.c.edit(
                filepath=f"src/components/{component_spec['name']}.vue",
                prompt=f"Apply these Tailwind classes to the component: {tailwind_classes} {layout_info}. Ensure <script> comes before <template>, avoid <style> unless necessary, and place all type definitions in ./types folder."
            )

            print(f"Successfully generated component {component_spec['name']} from Figma")
            return component_spec

        except Exception as e:
            print(f"Error generating component from Figma: {str(e)}")
            raise

    def _convert_layout_to_tailwind(self, layout: Dict) -> str:
        """Convert layout specs to Tailwind classes"""
        classes = []

        if layout.get("type") == "HORIZONTAL":
            classes.append("flex flex-row")
        elif layout.get("type") == "VERTICAL":
            classes.append("flex flex-col")

        if "spacing" in layout:
            spacing_value = layout["spacing"]
            if spacing_value <= 4:
                classes.append("gap-1")
            elif spacing_value <= 8:
                classes.append("gap-2")
            elif spacing_value <= 16:
                classes.append("gap-4")
            else:
                classes.append("gap-6")

        if "width" in layout and layout["width"] == "100%":
            classes.append("w-full")

        return " ".join(classes)

if __name__ == "__main__":
    import asyncio
    import sys

    async def main():
        if len(sys.argv) != 3:
            print("Usage: python figma_integration.py [figma_token] [figma_url]")
            sys.exit(1)

        figma_token = sys.argv[1]
        figma_url = sys.argv[2]

        agent = FigmaToVueAgent(figma_token)
        await agent.generate_component(figma_url)

    asyncio.run(main())
