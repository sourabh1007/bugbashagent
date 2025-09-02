import sys

# Read the file
with open('agents/code_generator.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the start and end of the method
start_line = None
end_line = None
for i, line in enumerate(lines):
    if 'def _get_single_scenario_prompt(self, language: str, context: Dict[str, Any] = None) -> str:' in line:
        start_line = i
    elif start_line is not None and line.strip().startswith('def ') and not '_get_single_scenario_prompt' in line:
        end_line = i
        break

if start_line is not None and end_line is not None:
    new_lines = lines[:start_line] + lines[end_line:]
    with open('agents/code_generator.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f'Removed method from line {start_line+1} to {end_line}')
else:
    print('Method boundaries not found')
