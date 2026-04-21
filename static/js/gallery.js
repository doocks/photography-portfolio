// Gallery JavaScript for additional functionality

// ============================================================
// LOADING SCREEN
// ============================================================
window.addEventListener('load', () => {
    const loading = document.getElementById('loading');
    if (loading) {
        setTimeout(() => {
            loading.classList.add('hide');
            setTimeout(() => {
                if (loading && loading.parentNode) loading.remove();
            }, 500);
        }, 500);
    }
});

// ============================================================
// IMAGE LAZY LOADING
// ============================================================
const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            if (img.dataset.src) {
                img.src = img.dataset.src;
                img.classList.add('loaded');
                observer.unobserve(img);
            }
        }
    });
}, {
    rootMargin: '50px',
    threshold: 0.1
});

// Observe all images with data-src attribute
document.querySelectorAll('img[data-src]').forEach(img => {
    imageObserver.observe(img);
});

// ============================================================
// LIGHTBOX FUNCTIONALITY
// ============================================================
let currentPhotoIndex = 0;
let currentPhotos = [];

function openLightbox(src, title, desc, allPhotos = null, currentIdx = 0) {
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const lightboxTitle = document.getElementById('lightbox-title');
    const lightboxDesc = document.getElementById('lightbox-desc');
    
    if (!lightbox || !lightboxImg) return;
    
    // Set current photo
    lightboxImg.src = src;
    if (lightboxTitle) lightboxTitle.innerText = title || '';
    if (lightboxDesc) lightboxDesc.innerText = desc || '';
    
    // Store all photos for navigation
    if (allPhotos) {
        currentPhotos = allPhotos;
        currentPhotoIndex = currentIdx;
    }
    
    // Show lightbox
    lightbox.classList.add('active');
    document.body.style.overflow = 'hidden';
    
    // Update navigation buttons visibility
    updateNavigationButtons();
}

function closeLightbox() {
    const lightbox = document.getElementById('lightbox');
    if (lightbox) {
        lightbox.classList.remove('active');
    }
    document.body.style.overflow = '';
}

function nextPhoto() {
    if (currentPhotos.length > 0 && currentPhotoIndex < currentPhotos.length - 1) {
        currentPhotoIndex++;
        const photo = currentPhotos[currentPhotoIndex];
        const lightboxImg = document.getElementById('lightbox-img');
        const lightboxTitle = document.getElementById('lightbox-title');
        const lightboxDesc = document.getElementById('lightbox-desc');
        
        if (lightboxImg) lightboxImg.src = photo.image || photo.src;
        if (lightboxTitle) lightboxTitle.innerText = photo.title || '';
        if (lightboxDesc) lightboxDesc.innerText = photo.description || photo.desc || '';
        
        updateNavigationButtons();
    }
}

function prevPhoto() {
    if (currentPhotos.length > 0 && currentPhotoIndex > 0) {
        currentPhotoIndex--;
        const photo = currentPhotos[currentPhotoIndex];
        const lightboxImg = document.getElementById('lightbox-img');
        const lightboxTitle = document.getElementById('lightbox-title');
        const lightboxDesc = document.getElementById('lightbox-desc');
        
        if (lightboxImg) lightboxImg.src = photo.image || photo.src;
        if (lightboxTitle) lightboxTitle.innerText = photo.title || '';
        if (lightboxDesc) lightboxDesc.innerText = photo.description || photo.desc || '';
        
        updateNavigationButtons();
    }
}

function updateNavigationButtons() {
    const prevBtn = document.getElementById('lightbox-prev');
    const nextBtn = document.getElementById('lightbox-next');
    
    if (prevBtn) {
        prevBtn.style.display = currentPhotoIndex > 0 ? 'flex' : 'none';
    }
    if (nextBtn) {
        nextBtn.style.display = currentPhotoIndex < currentPhotos.length - 1 ? 'flex' : 'none';
    }
}

// Keyboard navigation for lightbox
document.addEventListener('keydown', (e) => {
    const lightbox = document.getElementById('lightbox');
    if (lightbox && lightbox.classList.contains('active')) {
        if (e.key === 'Escape') {
            closeLightbox();
        } else if (e.key === 'ArrowLeft') {
            prevPhoto();
        } else if (e.key === 'ArrowRight') {
            nextPhoto();
        }
    }
});

// Close lightbox when clicking on background
document.addEventListener('click', (e) => {
    const lightbox = document.getElementById('lightbox');
    if (lightbox && lightbox.classList.contains('active')) {
        if (e.target === lightbox || e.target.classList.contains('close-lightbox')) {
            closeLightbox();
        }
    }
});

// ============================================================
// GALLERY FILTERING
// ============================================================
function filterGallery(category) {
    const items = document.querySelectorAll('.gallery-item');
    const buttons = document.querySelectorAll('.filter-btn');
    
    // Update button styles
    buttons.forEach(btn => {
        const btnCategory = btn.getAttribute('data-filter') || btn.getAttribute('data-category');
        if (btnCategory === category) {
            btn.classList.remove('btn-outline');
            btn.classList.add('btn-primary');
        } else {
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-outline');
        }
    });
    
    // Filter items
    items.forEach(item => {
        const itemCategory = item.getAttribute('data-category');
        if (category === 'all' || itemCategory === category) {
            item.style.display = 'block';
            item.classList.add('show');
            item.classList.remove('hide');
        } else {
            item.style.display = 'none';
            item.classList.remove('show');
            item.classList.add('hide');
        }
    });
}

// ============================================================
// GALLERY ITEM HOVER EFFECTS
// ============================================================
document.querySelectorAll('.gallery-item').forEach(item => {
    const overlay = item.querySelector('.gallery-overlay');
    if (overlay) {
        item.addEventListener('mouseenter', () => {
            overlay.style.transform = 'translateY(0)';
        });
        item.addEventListener('mouseleave', () => {
            overlay.style.transform = 'translateY(100%)';
        });
        
        // Click on gallery item
        item.addEventListener('click', (e) => {
            if (e.target === overlay || overlay.contains(e.target)) {
                return;
            }
            const img = item.querySelector('img');
            const title = overlay.querySelector('h3')?.innerText || '';
            const desc = overlay.querySelector('p')?.innerText || '';
            if (img && img.src) {
                openLightbox(img.src, title, desc);
            }
        });
    }
});

// ============================================================
// FORM VALIDATION
// ============================================================
function validateBookingForm() {
    const name = document.getElementById('id_client_name')?.value;
    const email = document.getElementById('id_client_email')?.value;
    const phone = document.getElementById('id_client_phone')?.value;
    const eventDate = document.getElementById('id_event_date')?.value;
    
    if (!name || name.trim() === '') {
        alert('Please enter your name');
        return false;
    }
    
    if (!email || !email.includes('@')) {
        alert('Please enter a valid email address');
        return false;
    }
    
    if (!phone || phone.trim() === '') {
        alert('Please enter your phone number');
        return false;
    }
    
    if (!eventDate) {
        alert('Please select an event date');
        return false;
    }
    
    return true;
}

// ============================================================
// ACCESS CODE FORM HANDLING
// ============================================================
function handleAccessCodeSubmit() {
    const codeInput = document.getElementById('access_code');
    if (codeInput) {
        const code = codeInput.value.trim().toUpperCase();
        codeInput.value = code;
        
        if (!code) {
            alert('Please enter an access code');
            return false;
        }
        if (code.length < 4) {
            alert('Access code must be at least 4 characters');
            return false;
        }
    }
    return true;
}

// ============================================================
// MOBILE MENU TOGGLE
// ============================================================
function toggleMobileMenu() {
    const navLinks = document.getElementById('navLinks');
    if (navLinks) {
        navLinks.classList.toggle('active');
        navLinks.classList.toggle('show');
    }
}

// Close mobile menu when clicking outside
document.addEventListener('click', (e) => {
    const navLinks = document.getElementById('navLinks');
    const menuToggle = document.querySelector('.menu-toggle');
    
    if (navLinks && navLinks.classList.contains('active')) {
        if (!navLinks.contains(e.target) && !menuToggle?.contains(e.target)) {
            navLinks.classList.remove('active');
            navLinks.classList.remove('show');
        }
    }
});

// ============================================================
// SMOOTH SCROLLING
// ============================================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href && href !== '#' && href !== '#/' && href !== '#0') {
            const targetId = href.substring(1);
            const target = document.getElementById(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
                
                // Close mobile menu if open
                const navLinks = document.getElementById('navLinks');
                if (navLinks && navLinks.classList.contains('active')) {
                    navLinks.classList.remove('active');
                    navLinks.classList.remove('show');
                }
            }
        }
    });
});

// ============================================================
// AUTO-HIDE MESSAGES
// ============================================================
setTimeout(() => {
    const messages = document.querySelectorAll('.alert-success, .alert-error, .alert-warning');
    messages.forEach(msg => {
        setTimeout(() => {
            msg.style.transition = 'opacity 0.5s';
            msg.style.opacity = '0';
            setTimeout(() => {
                if (msg.parentNode) msg.remove();
            }, 500);
        }, 4000);
    });
}, 100);

// ============================================================
// INITIALIZE AOS (Animate on Scroll)
// ============================================================
if (typeof AOS !== 'undefined') {
    AOS.init({
        duration: 800,
        once: true,
        offset: 100
    });
}

// ============================================================
// BOOKING FORM PACKAGE PRESELECTION
// ============================================================
const urlParams = new URLSearchParams(window.location.search);
const packageId = urlParams.get('package');
if (packageId) {
    const packageSelect = document.getElementById('id_package');
    if (packageSelect) {
        packageSelect.value = packageId;
    }
}

// ============================================================
// EVENT DATE MINIMUM (Cannot book past dates)
// ============================================================
const eventDateInput = document.getElementById('id_event_date');
if (eventDateInput) {
    const today = new Date().toISOString().split('T')[0];
    eventDateInput.setAttribute('min', today);
}

// ============================================================
// CONSOLE LOG (For debugging - remove in production)
// ============================================================
console.log('Gallery JavaScript loaded successfully');