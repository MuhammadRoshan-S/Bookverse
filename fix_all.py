
import io
with io.open(r'f:\My projects\Bookverse\templates\base.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix My Orders dropdown (from prev bug)
lines = text.split('\n')
for i, line in enumerate(lines):
    if 'My Orders' in line:
        lines[i-2] = lines[i-2].replace('checkout', 'my_orders')
        break
text = '\n'.join(lines)

# Append JS fallback logic
js_script = '''
<script>
document.addEventListener('DOMContentLoaded', () => {
    const checkImage = (img) => {
        if (img.naturalWidth === 575 && img.naturalHeight === 750 && img.src.includes('zoom=0')) {
            img.src = img.src.replace('zoom=0', 'zoom=1');
        }
    };
    document.querySelectorAll('img').forEach(img => {
        if (img.complete) { checkImage(img); } 
        else { img.addEventListener('load', () => checkImage(img)); }
    });
});
</script>
</body>'''
text = text.replace('</body>', js_script)

with io.open(r'f:\My projects\Bookverse\templates\base.html', 'w', encoding='utf-8') as f:
    f.write(text)

