# [Analysis Name] Template

Use this template when creating new analyses for 3I/ATLAS research.

## Folder Structure for New Analysis

When creating a new analysis called `[analysis-name]`, create these folders:

```
analyses/[analysis-name]/           # Main analysis code and notebooks
data/[analysis-name]/              # Analysis-specific datasets  
results/[analysis-name]/           # Analysis outputs and findings
visualizations/[analysis-name]/    # Analysis-specific plots
docs/[analysis-name]/              # Analysis documentation
```

## Required Files

### In `analyses/[analysis-name]/`:
- `[analysis-name].py` - Main analysis script
- `[analysis-name]_analysis.ipynb` - Interactive notebook
- `README.md` - Brief analysis overview
- `modules/` - Analysis-specific code modules (if needed)

### In `docs/[analysis-name]/`:
- `README.md` - Detailed documentation (use template below)
- `methodology.md` - Detailed methods description
- `references.md` - Citations and sources

### In `data/[analysis-name]/`:
- Raw data files
- Processed datasets
- Data README explaining sources

### In `results/[analysis-name]/`:
- Summary reports
- Statistical outputs  
- Numerical results

### In `visualizations/[analysis-name]/`:
- Publication-quality figures
- Interactive plots
- Figure captions and descriptions

## Documentation Template

Copy this template to `docs/[analysis-name]/README.md`:

```markdown
# [Analysis Name]

**Brief description of what this analysis investigates.**

## Executive Summary

[2-3 sentences summarizing key findings]

## Research Question

[Clear statement of what you're investigating]

## Methodology

### Data Sources
- [List data sources]

### Analysis Methods  
- [Describe analytical approach]

### Computational Tools
- [List key software/libraries used]

## Key Results

| Parameter | Value | Context |
|-----------|--------|---------|
| [Key Finding 1] | [Value] | [Interpretation] |
| [Key Finding 2] | [Value] | [Interpretation] |

## Scientific Significance

### Physical Interpretation
[What do the results mean physically?]

### Implications
1. [Implication 1]
2. [Implication 2]
3. [Implication 3]

## Analysis Files

### Notebooks
- `[analysis-name]_analysis.ipynb` - [Description]

### Scripts  
- `[analysis-name].py` - [Description]

### Data Files
- [List key data files and their contents]

### Results
- [List key result files]

### Visualizations
- [List key figures and plots]

## Reproducibility

### Quick Start
```bash
cd analyses/[analysis-name]/
jupyter notebook [analysis-name]_analysis.ipynb
# or
python [analysis-name].py
```

### Dependencies
[List specific requirements beyond main requirements.txt]

## Educational Use

[How can this analysis be used for education?]

## References

[Key citations and sources]

## Citation

```bibtex
@article{3i_atlas_[analysis_name]_2025,
  title={[Full Title]},
  author={[Author Names]},
  journal={3I/ATLAS Research Repository},
  year={2025},
  url={https://github.com/[username]/3I_ATLAS/tree/main/analyses/[analysis-name]}
}
```
```

## Coding Standards

### Python Scripts
- Use consistent imports and structure
- Include docstrings for all functions
- Follow PEP 8 style guidelines
- Add type hints where appropriate

### Notebooks
- Clear markdown explanations between code cells
- Publication-quality plots with proper labels
- Executive summary at the beginning
- Conclusions section at the end

### Data Files
- Include metadata and source information
- Use standard formats (CSV, JSON, HDF5)
- Document units and coordinate systems
- Provide data dictionaries when needed

## Quality Checklist

Before submitting a new analysis, verify:

- [ ] All folders created with correct structure
- [ ] Documentation follows template format
- [ ] Code includes proper error handling
- [ ] Results are reproducible
- [ ] Visualizations are publication-quality
- [ ] Scientific conclusions are clearly stated
- [ ] References and citations included
- [ ] README updated with new analysis

## Example Analyses

Use these as references:
- `jupiter-intercept/` - Complete orbital mechanics analysis
- [Future analyses will be listed here]

---

*Template last updated: December 2025*




