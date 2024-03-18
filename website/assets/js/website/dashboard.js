/**
 * Dashboard JavaScript | Cannlytics Website
 * Copyright (c) 2024 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 2/20/2024
 * Updated: 2/20/2024
 * License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>
 */
import { Tooltip } from 'bootstrap';

export const dashboard = {

  initializeDashboard() {
    /**
     * Initialize the dashboard page.
     */
    document.getElementById('toggleSidebar').addEventListener('click', function() {
      const sidebar = document.getElementById('sidebar');
      sidebar.classList.toggle('collapsed');

      // Adjust main content margin based on sidebar state
      const mainContent = document.querySelector('.main-content');
      if (sidebar.classList.contains('collapsed')) {
        mainContent.style.marginLeft = '80px';
        // mainContent.classList.remove('expanded-margin');
      } else {
        mainContent.style.marginLeft = '225px';
        // mainContent.classList.add('expanded-margin');
      }
    
      // Adjust aria-labels based on collapse state
      const isCollapsed = sidebar.classList.contains('collapsed');
      document.querySelectorAll('#sidebar .nav-link').forEach(link => {
        try {
          const label = link.querySelector('.link-text').textContent.trim();
          link.setAttribute('aria-label', isCollapsed ? label : '');
        } catch(error) {
          // Pass
        }
      });

      // Add tooltips.
      // if (isCollapsed) {
      //   new Tooltip(document.querySelector('#toggleSidebar'), {
      //     title: 'Expand',
      //     placement: 'right'
      //   });
      //   // Initialize tooltips for each sidebar link
      //   document.querySelectorAll('#sidebar .nav-link').forEach(link => {
      //     new Tooltip(link, {
      //       title: link.getAttribute('aria-label'),
      //       placement: 'right'
      //     });
      //   });
      // } else {
      //   // Dispose tooltips when un-collapsing.
      //   Tooltip.getInstance(document.querySelector('#toggleSidebar')).dispose();
      //   document.querySelectorAll('#sidebar .nav-link').forEach(link => {
      //     const tooltipInstance = Tooltip.getInstance(link);
      //     if (tooltipInstance) {
      //       tooltipInstance.dispose();
      //     }
      //   });
      // }

      // Change the icon based on the collapsed state.
      if (isCollapsed) {
        this.innerHTML = '<i class="bi bi-chevron-right"></i>';
      } else {
        this.innerHTML = '<i class="bi bi-chevron-left"></i>';
      }
    });
  },

};