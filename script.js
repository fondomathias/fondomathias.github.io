document.addEventListener('DOMContentLoaded', () => {
    // Navigation active state logic and smooth scrolling offset
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.content-section');
    const headerHeight = document.querySelector('.top-header').offsetHeight;

    window.addEventListener('scroll', () => {
        let current = '';

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            // Add a small offset to ensure the section is considered active a bit earlier
            if (pageYOffset >= sectionTop - headerHeight - 100) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });

        // Handle "Homepage" case specifically when scrolled to the very top
        if (pageYOffset < 100) {
            navLinks.forEach(link => link.classList.remove('active'));
            const homeLink = document.querySelector('.nav-link[href="#homepage"]');
            if (homeLink) homeLink.classList.add('active');
        }
    });

    // Smooth scroll offset adjustment to account for sticky navbar
    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');

            // Only apply this logic to anchor links (starting with #)
            if (targetId.startsWith('#')) {
                e.preventDefault();

                if (targetId === '#homepage') {
                    // Always scroll to the absolute top for the homepage
                    window.scrollTo({
                        top: 0,
                        behavior: 'smooth'
                    });
                } else {
                    const targetSection = document.querySelector(targetId);
                    if (targetSection) {
                        const topPosition = targetSection.getBoundingClientRect().top + window.pageYOffset - headerHeight - 20;

                        window.scrollTo({
                            top: topPosition,
                            behavior: 'smooth'
                        });
                    }
                }
            }
        });
    });

    // Accordion for papers
    const paperHeaders = document.querySelectorAll('.paper-header');
    paperHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const content = header.nextElementSibling;

            // Toggle active classes
            header.classList.toggle('active');
            if (content) {
                content.classList.toggle('active');
            }
        });
    });
});
