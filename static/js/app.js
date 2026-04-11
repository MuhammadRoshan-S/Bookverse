/* =============================================
   BOOKVERSE — App JavaScript
   ============================================= */

// ── Custom Cursor ────────────────────────────
const cursor = document.getElementById('cursor');
const cursorFollower = document.getElementById('cursorFollower');
let mouseX = 0, mouseY = 0, followerX = 0, followerY = 0;

if (cursor && cursorFollower) {
  document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX; mouseY = e.clientY;
    cursor.style.left = mouseX + 'px';
    cursor.style.top = mouseY + 'px';
  });
  function animateFollower() {
    followerX += (mouseX - followerX) * 0.12;
    followerY += (mouseY - followerY) * 0.12;
    cursorFollower.style.left = followerX + 'px';
    cursorFollower.style.top = followerY + 'px';
    requestAnimationFrame(animateFollower);
  }
  animateFollower();
  document.querySelectorAll('a, button, .bento-card, .book-card, .cat-card, .carousel-item').forEach(el => {
    el.addEventListener('mouseenter', () => cursorFollower.classList.add('hovering'));
    el.addEventListener('mouseleave', () => cursorFollower.classList.remove('hovering'));
  });
}

// ── Navbar Scroll ────────────────────────────
const nav = document.getElementById('nav');
if (nav) window.addEventListener('scroll', () => nav.classList.toggle('scrolled', window.scrollY > 60));

// ── CSRF Helper ──────────────────────────────
function getCsrf() {
  const el = document.querySelector('[name=csrfmiddlewaretoken]');
  if (el) return el.value;
  const match = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
  return match ? match.trim().split('=')[1] : '';
}

// ── Toast ─────────────────────────────────────
function showToast(msg, duration = 3000) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), duration);
}

// ── Profile Dropdown ──────────────────────────
const profileBtn = document.getElementById('profileBtn');
const profileDropdown = document.getElementById('profileDropdown');
if (profileBtn && profileDropdown) {
  profileBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    profileDropdown.classList.toggle('open');
  });
  document.addEventListener('click', (e) => {
    if (!profileDropdown.contains(e.target) && e.target !== profileBtn) {
      profileDropdown.classList.remove('open');
    }
  });
}

// ── Hamburger / Mobile Nav ────────────────────
const hamburger = document.getElementById('navHamburger');
const mobileDrawer = document.getElementById('mobileNavDrawer');
if (hamburger && mobileDrawer) {
  hamburger.addEventListener('click', () => {
    const open = mobileDrawer.classList.toggle('open');
    hamburger.classList.toggle('open', open);
    mobileDrawer.setAttribute('aria-hidden', String(!open));
    document.body.style.overflow = open ? 'hidden' : '';
  });
  // Close drawer when a link is clicked
  mobileDrawer.querySelectorAll('a').forEach(a =>
    a.addEventListener('click', () => {
      mobileDrawer.classList.remove('open');
      hamburger.classList.remove('open');
      document.body.style.overflow = '';
    })
  );
}

// ── Wishlist Toggle ────────────────────────────
function toggleWishlist(bookId, btn) {
  fetch(`/wishlist/toggle/${bookId}/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': getCsrf() },
    credentials: 'same-origin',
  })
  .then(r => {
    if (r.status === 401) {
      showToast('Please login to add to wishlist');
      setTimeout(() => window.location.href = '/accounts/login/', 1200);
      return null;
    }
    return r.json();
  })
  .then(data => {
    if (!data) return;
    if (data.success) {
      if (btn) {
        btn.classList.toggle('wishlisted', data.wishlisted);
        btn.title = data.wishlisted ? 'Remove from wishlist' : 'Add to wishlist';
        btn.querySelector('svg')?.setAttribute('fill', data.wishlisted ? 'currentColor' : 'none');
      }
      showToast(data.message);
    }
  })
  .catch(() => showToast('Something went wrong.'));
}

// ── Cart Drawer ───────────────────────────────
const cartDrawer = document.getElementById('cartDrawer');
const cartOverlay = document.getElementById('cartOverlay');
let cartOpen = false;

function toggleCart() {
  if (!cartDrawer) return;
  cartOpen = !cartOpen;
  cartDrawer.classList.toggle('open', cartOpen);
  cartOverlay.classList.toggle('open', cartOpen);
  document.body.style.overflow = cartOpen ? 'hidden' : '';
  if (cartOpen) loadCartDrawer();
}

const cartBtn = document.getElementById('cartBtn');
if (cartBtn) cartBtn.addEventListener('click', toggleCart);

function loadCartDrawer() {
  fetch('/cart/json/')
    .then(r => r.json())
    .then(data => renderCartDrawer(data))
    .catch(() => {});
}

function renderCartDrawer(data) {
  const itemsEl = document.getElementById('drawerCartItems');
  const emptyEl = document.getElementById('drawerCartEmpty');
  const footerEl = document.getElementById('drawerCartFooter');
  const totalEl = document.getElementById('drawerCartTotal');

  if (!itemsEl) return;

  // Clear old items except empty state
  itemsEl.querySelectorAll('.drawer-item').forEach(el => el.remove());

  if (!data.items || data.items.length === 0) {
    if (emptyEl) emptyEl.style.display = 'block';
    if (footerEl) footerEl.style.display = 'none';
    return;
  }

  if (emptyEl) emptyEl.style.display = 'none';
  if (footerEl) footerEl.style.display = 'block';
  if (totalEl) totalEl.textContent = '₹' + parseFloat(data.total).toFixed(2);

  data.items.forEach(item => {
    const div = document.createElement('div');
    div.className = 'drawer-item';
    div.id = `drawer-item-${item.id}`;
    div.innerHTML = `
      <img src="${item.cover}" alt="${item.title}" class="drawer-item-img"
           onerror="this.style.background='var(--bg-3)'; this.src='';" />
      <div class="drawer-item-info">
        <p class="drawer-item-title">${item.title}</p>
        <p class="drawer-item-author">${item.authors}</p>
        <p class="drawer-item-qty">Qty: ${item.quantity}</p>
      </div>
      <span class="drawer-item-price">₹${parseFloat(item.subtotal).toFixed(2)}</span>
      <button class="drawer-item-remove" onclick="removeFromCart(${item.id}, this)" title="Remove">✕</button>
    `;
    itemsEl.appendChild(div);
  });

  // Update count badges
  updateCartBadge(data.count);
}

function updateCartBadge(count) {
  document.querySelectorAll('.cart-count, #cartCountBadge').forEach(el => {
    el.textContent = count;
  });
}

// ── Add to Cart (AJAX) ────────────────────────
function addToCart(bookId, btn) {
  const csrfToken = getCsrf();
  const originalText = btn ? btn.textContent : '';
  if (btn) { btn.textContent = '...'; btn.disabled = true; }

  fetch(`/cart/add/${bookId}/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': csrfToken, 'Content-Type': 'application/json' },
    credentials: 'same-origin',
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      updateCartBadge(data.cart_count);
      showToast('📚 ' + data.message);
      if (btn) {
        btn.textContent = '✓';
        setTimeout(() => { btn.textContent = originalText; btn.disabled = false; }, 2000);
      }
      if (cartOpen) loadCartDrawer();
    }
  })
  .catch(() => {
    showToast('Something went wrong. Try again.');
    if (btn) { btn.textContent = originalText; btn.disabled = false; }
  });
}

// ── Remove from Cart ─────────────────────────
function removeFromCart(itemId, el) {
  fetch(`/cart/remove/${itemId}/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': getCsrf() },
    credentials: 'same-origin',
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      // Remove from drawer
      const drawerItem = document.getElementById(`drawer-item-${itemId}`);
      if (drawerItem) drawerItem.remove();
      // Remove from cart page
      const pageItem = document.getElementById(`cart-item-${itemId}`);
      if (pageItem) pageItem.remove();

      updateCartBadge(data.cart_count);
      const totalEl = document.getElementById('drawerCartTotal');
      if (totalEl) totalEl.textContent = '₹' + parseFloat(data.cart_total).toFixed(2);
      const summaryTotal = document.getElementById('summaryTotal');
      if (summaryTotal) summaryTotal.textContent = '₹' + parseFloat(data.cart_total).toFixed(2);

      if (data.cart_count === 0) {
        const emptyEl = document.getElementById('drawerCartEmpty');
        const footerEl = document.getElementById('drawerCartFooter');
        if (emptyEl) emptyEl.style.display = 'block';
        if (footerEl) footerEl.style.display = 'none';
      }
      showToast('Item removed');
    }
  });
}

// ── Update Cart Quantity ──────────────────────
function updateQty(itemId, delta) {
  const qtyEl = document.getElementById(`qty-${itemId}`);
  if (!qtyEl) return;
  const newQty = Math.max(0, parseInt(qtyEl.textContent) + delta);

  fetch(`/cart/update/${itemId}/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': getCsrf(), 'Content-Type': 'application/json' },
    credentials: 'same-origin',
    body: JSON.stringify({ quantity: newQty }),
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      if (newQty === 0) {
        const row = document.getElementById(`cart-item-${itemId}`);
        if (row) row.remove();
      } else {
        qtyEl.textContent = newQty;
        const subEl = document.getElementById(`sub-${itemId}`);
        if (subEl) subEl.textContent = '₹' + parseFloat(data.subtotal).toFixed(2);
      }
      updateCartBadge(data.cart_count);
      const totalEl = document.getElementById('summaryTotal');
      if (totalEl) totalEl.textContent = '₹' + parseFloat(data.cart_total).toFixed(2);
    }
  });
}

// ── Checkout & Razorpay ───────────────────────
const checkoutForm = document.getElementById('checkoutForm');
if (checkoutForm) {
  checkoutForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const payBtn = document.getElementById('payBtn');
    if (payBtn) { payBtn.textContent = 'Processing...'; payBtn.disabled = true; }
    const formData = new FormData(checkoutForm);

    fetch('/checkout/', {
      method: 'POST',
      body: formData,
      headers: { 'X-CSRFToken': getCsrf() },
      credentials: 'same-origin',
    })
    .then(r => r.json())
    .then(data => {
      const rzpKey = window.RAZORPAY_KEY || data.razorpay_key;
      const options = {
        key: rzpKey,
        amount: data.amount,
        currency: data.currency,
        name: 'Bookverse',
        description: 'Book Purchase',
        order_id: data.razorpay_order_id,
        prefill: { name: data.name, email: data.email, contact: data.phone },
        theme: { color: '#c8392b' },
        handler: function(response) {
          fetch('/payment-success/', {
            method: 'POST',
            headers: { 'X-CSRFToken': getCsrf(), 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_order_id: response.razorpay_order_id,
              razorpay_signature: response.razorpay_signature,
            }),
          })
          .then(r => r.json())
          .then(result => {
            if (result.success) window.location.href = result.redirect;
            else showToast('Payment verification failed. Contact support.');
          });
        },
        modal: { ondismiss: () => {
          showToast('Payment cancelled.');
          if (payBtn) { payBtn.textContent = 'PAY SECURELY →'; payBtn.disabled = false; }
        }}
      };
      const rzp = new Razorpay(options);
      rzp.open();
    })
    .catch(() => {
      showToast('Error connecting to payment gateway.');
      if (payBtn) { payBtn.textContent = 'PAY SECURELY →'; payBtn.disabled = false; }
    });
  });
}

// ── Book Filter Buttons ───────────────────────
function setFilter(filter, btn) {
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.book-card[data-category]').forEach(card => {
    card.style.display = (filter === 'All' || card.dataset.category === filter) ? '' : 'none';
  });
}

// ── Scroll Reveal ────────────────────────────
const reveals = document.querySelectorAll('.reveal');
if (reveals.length) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); observer.unobserve(e.target); } });
  }, { threshold: 0.08, rootMargin: '0px 0px -30px 0px' });
  reveals.forEach(el => observer.observe(el));
}

// ── Auto-dismiss Django Messages ─────────────
document.querySelectorAll('.message').forEach(msg => {
  setTimeout(() => {
    msg.style.transition = 'all 0.4s ease';
    msg.style.opacity = '0'; msg.style.transform = 'translateX(100%)';
    setTimeout(() => msg.remove(), 400);
  }, 4000);
});

// ── Active Nav Link on Scroll ─────────────────
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-link[data-section]');
if (sections.length && navLinks.length) {
  const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        navLinks.forEach(l => l.classList.remove('active'));
        const al = document.querySelector(`.nav-link[data-section="${entry.target.id}"]`);
        if (al) al.classList.add('active');
      }
    });
  }, { threshold: 0.4 });
  sections.forEach(s => sectionObserver.observe(s));
}

// ══════════════════════════════════════════════
// ── 3D Book Carousel ─────────────────────────
// ══════════════════════════════════════════════
(function() {
  const track = document.getElementById('carouselTrack');
  if (!track) return;

  const items = Array.from(track.querySelectorAll('.carousel-item'));
  if (!items.length) return;

  const isMobile = window.innerWidth <= 768;
  const total = items.length;
  let current = Math.floor(total / 2);

  // Desktop uses bigger offsets; mobile uses compact values to fit the screen
  function getPosition(offset) {
    const absOff = Math.abs(offset);
    if (isMobile) {
      if (absOff === 0) return { x: 0,           rotY: 0,           scale: 1,    opacity: 1,    z: 10, cls: 'active' };
      if (absOff === 1) return { x: offset * 100, rotY: offset * -38, scale: 0.75, opacity: 0.85, z: 7,  cls: 'side'   };
      if (absOff === 2) return { x: offset * 175, rotY: offset * -48, scale: 0.55, opacity: 0.40, z: 5,  cls: 'side'   };
      return                    { x: offset * 230, rotY: offset * -55, scale: 0.35, opacity: 0.10, z: 1,  cls: 'far'    };
    }
    if (absOff === 0) return { x: 0,            rotY: 0,           scale: 1,    opacity: 1,    z: 10, cls: 'active' };
    if (absOff === 1) return { x: offset * 165, rotY: offset * -40, scale: 0.82, opacity: 0.88, z: 7,  cls: 'side'   };
    if (absOff === 2) return { x: offset * 270, rotY: offset * -50, scale: 0.66, opacity: 0.55, z: 5,  cls: 'side'   };
    if (absOff === 3) return { x: offset * 350, rotY: offset * -56, scale: 0.52, opacity: 0.28, z: 3,  cls: 'far'    };
    return                    { x: offset * 410, rotY: offset * -60, scale: 0.38, opacity: 0.10, z: 1,  cls: 'far'    };
  }

  function updateCarousel(animate = true) {
    items.forEach((item, i) => {
      const offset = i - current;
      const pos = getPosition(offset);
      item.className = 'carousel-item ' + pos.cls;
      item.style.transform = `
        translateX(-50%) translateY(-50%)
        translateX(${pos.x}px)
        rotateY(${pos.rotY}deg)
        scale(${pos.scale})
      `;
      item.style.opacity = pos.opacity;
      item.style.zIndex = pos.z;
      item.style.transition = animate ? 'transform 0.65s cubic-bezier(0.25,0.46,0.45,0.94), opacity 0.65s ease' : 'none';
    });
  }

  updateCarousel(false);

  document.getElementById('carouselNext')?.addEventListener('click', () => {
    current = (current + 1) % total;
    updateCarousel();
  });
  document.getElementById('carouselPrev')?.addEventListener('click', () => {
    current = (current - 1 + total) % total;
    updateCarousel();
  });

  // Click a non-active item to bring it to center
  items.forEach((item, i) => {
    item.querySelector('.carousel-card')?.addEventListener('click', () => {
      if (i !== current) { current = i; updateCarousel(); }
    });
  });

  // Touch swipe support for mobile
  if (isMobile) {
    const scene = track.closest('.carousel-scene') || track;
    let touchStartX = 0;
    scene.addEventListener('touchstart', e => {
      touchStartX = e.touches[0].clientX;
    }, { passive: true });
    scene.addEventListener('touchend', e => {
      const diff = touchStartX - e.changedTouches[0].clientX;
      if (Math.abs(diff) > 40) {
        current = diff > 0 ? (current + 1) % total : (current - 1 + total) % total;
        updateCarousel();
      }
    }, { passive: true });
  }

  // Auto-advance
  let autoTimer = setInterval(() => {
    current = (current + 1) % total;
    updateCarousel();
  }, 3500);

  track.addEventListener('mouseenter', () => clearInterval(autoTimer));
  track.addEventListener('mouseleave', () => {
    autoTimer = setInterval(() => { current = (current + 1) % total; updateCarousel(); }, 3500);
  });
})();


// ══════════════════════════════════════════════
// ── Category Horizontal Slider ───────────────
// ══════════════════════════════════════════════
(function() {
  const slider = document.getElementById('catSlider');
  const prevBtn = document.getElementById('catPrev');
  const nextBtn = document.getElementById('catNext');
  if (!slider) return;

  const slideWidth = 300; // 280 + 20 gap
  let currentOffset = 0;
  const maxOffset = () => Math.max(0, slider.children.length * slideWidth - slider.parentElement.clientWidth + 120);

  function moveCat(dir) {
    currentOffset = Math.max(0, Math.min(maxOffset(), currentOffset + dir * slideWidth * 2));
    slider.style.transform = `translateX(-${currentOffset}px)`;
  }

  if (prevBtn) prevBtn.addEventListener('click', () => moveCat(-1));
  if (nextBtn) nextBtn.addEventListener('click', () => moveCat(1));

  // Drag to scroll
  let startX = 0, dragging = false;
  const wrap = slider.parentElement;
  wrap.addEventListener('mousedown', e => { dragging = true; startX = e.clientX; });
  window.addEventListener('mouseup', () => { dragging = false; });
  window.addEventListener('mousemove', e => {
    if (!dragging) return;
    const diff = startX - e.clientX;
    currentOffset = Math.max(0, Math.min(maxOffset(), currentOffset + diff * 0.5));
    slider.style.transform = `translateX(-${currentOffset}px)`;
    startX = e.clientX;
  });
})();
