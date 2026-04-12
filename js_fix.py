
import io
with io.open(r'f:\My projects\Bookverse\static\js\app.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''    .then(data => {
      if (data.success) {
        updateCartBadge(data.cart_count);'''

repl = '''    .then(data => {
      if (!data.success) {
        if (btn) { btn.textContent = originalText; btn.disabled = false; }
        showToast('? ' + (data.message || 'Action failed'));
        return;
      }
      if (data.success) {
        updateCartBadge(data.cart_count);'''

text = text.replace(target, repl)
with io.open(r'f:\My projects\Bookverse\static\js\app.js', 'w', encoding='utf-8') as f:
    f.write(text)

