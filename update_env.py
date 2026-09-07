import os

env_path = '.env'
key = 'ELEVENLABS_API_KEY'
value = 'sk_11540ed8f87bd499b4f216ad860629c495cf18b0042b6ad8'

try:
    lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()

    new_lines = []
    key_found = False
    
    for line in lines:
        if line.strip().startswith(f'{key}='):
            new_lines.append(f'{key}={value}\n')
            key_found = True
        else:
            new_lines.append(line)
            
    if not key_found:
        if new_lines and not new_lines[-1].endswith('\n'):
            new_lines[-1] += '\n'
        new_lines.append(f'{key}={value}\n')

    with open(env_path, 'w') as f:
        f.writelines(new_lines)
        
    print(f"Successfully updated {key} in {env_path}")

except Exception as e:
    print(f"Error updating .env: {e}")
