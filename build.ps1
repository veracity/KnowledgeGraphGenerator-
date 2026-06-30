# Builds a standalone single-file executable with Nuitka.
#
# Usage:
#   .\build.ps1            # one-file build (default)
#   .\build.ps1 -OneDir    # faster-starting one-folder build
#
# Output goes to .\build\

param(
    [switch]$OneDir
)

$ErrorActionPreference = "Stop"

$common = @(
    "--standalone",
    "--enable-plugin=tk-inter",
    "--windows-console-mode=disable",
    "--company-name=KnowledgeGraphGenerator",
    "--product-name=Knowledge Graph Generator",
    "--file-version=0.1.0",
    "--product-version=0.1.0",
    "--output-dir=build",
    "--output-filename=KnowledgeGraphGenerator",
    "--assume-yes-for-downloads"
)

if (-not $OneDir) {
    $common += "--onefile"
}

uv run python -m nuitka @common main.py
