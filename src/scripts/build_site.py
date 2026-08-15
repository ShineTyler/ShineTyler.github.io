"""Compatibility entry point — delegates to the sitebuild package.

Kept at this path so `npm run build` and the GitHub Actions workflow
(`python src/scripts/build_site.py`) keep working unchanged.
"""
from sitebuild.build import main

if __name__ == "__main__":
    main()
