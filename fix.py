
import io
with io.open(r'f:\My projects\Bookverse\templates\base.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'My Orders' in line:
        lines[i-2] = lines[i-2].replace('checkout', 'my_orders')
        break
with io.open(r'f:\My projects\Bookverse\templates\base.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

