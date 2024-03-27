/**
 * Theme JavaScript | Cannlytics Console
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 12/6/2020
 * Updated: 12/14/2021
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 */
import { hasClass } from '../utils.js';

export const theme = {

  changeTheme() {
    /**
     * Change the UI theme.
     */
    let theme = localStorage.getItem('theme');
    if (!theme) {
      const hours = new Date().getHours();
      const dayTime = hours > 6 && hours < 20;
      theme = dayTime ? 'light' : 'dark';
    }
    const newTheme = (theme === 'light') ? 'dark' : 'light';
    this.toggleTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  },

  getTheme() {
    /**
     * Get the current theme.
     */
    return (document.body.classList.contains('dark')) ? 'dark' : 'light';
  },

  setInitialTheme () {
    /**
     * Set th initial UI theme.
     */
    console.log('Setting initial theme...');
    if (typeof(Storage) !== 'undefined') {
      const theme = localStorage.getItem('theme');
      if (!theme) {
        const hours = new Date().getHours();
        const dayTime = hours > 6 && hours < 20;
        if (!dayTime) this.toggleTheme('dark');
        return;
      }
      this.toggleTheme(theme);
      localStorage.setItem('theme', theme);
    }
  },

  setTableTheme() {
    /**
     * Set the appropriate theme for tables based on the current theme,
     * toggling the Ag-Grid theme too.
     */
    let nuisanceTableClass = 'ag-theme-quartz-dark';
    let finalTableClass = 'ag-theme-quartz';
    if (hasClass(document.body, 'dark')) {
      nuisanceTableClass = 'ag-theme-quartz';
      finalTableClass = 'ag-theme-quartz-dark';
    }
    let tables = document.getElementsByClassName(nuisanceTableClass);
    [...tables].forEach( x => x.classList.add(finalTableClass) );
    [...tables].forEach( x => x.classList.remove(nuisanceTableClass) );
  },

  toggleTheme(theme) {
    /**
     * Toggle the UI theme, toggling the AG-Grid table class too.
     */
    let currentTableClass = 'ag-theme-quartz';
    let newTableClass = 'ag-theme-quartz-dark';
    if (theme === 'light') {
      document.body.className = 'base';
      currentTableClass = 'ag-theme-quartz-dark';
      newTableClass = 'ag-theme-quartz';
    } else {
      document.body.classList.add('dark');
    }
    let tables = document.getElementsByClassName(currentTableClass);
    [...tables].forEach( x => x.classList.add(newTableClass) );
    [...tables].forEach( x => x.classList.remove(currentTableClass) );
  }

}
