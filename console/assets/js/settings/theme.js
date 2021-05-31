/**
 * Theme JavaScript | Cannlytics Console
 * Author: Keegan Skeate
 * Created: 12/6/2020
 * Updated: 4/24/2021
 */


export const theme = {


  changeTheme() {
    /*
     * Change the UI theme.
     */
    var theme = localStorage.getItem('theme');
    if (!theme) {
      var hours = new Date().getHours();
      var dayTime = hours > 6 && hours < 20;
      theme = dayTime ? 'light' : 'dark';
    }
    var newTheme = (theme === 'light') ? 'dark' : 'light';
    this.toggleTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  },


  getTheme() {
    /*
     * Get the current theme.
     */
    return (document.body.classList.contains('dark')) ? 'dark' : 'light';
  },


  setInitialTheme () {
    /*
     * Set th initial UI theme.
     */
    if (typeof(Storage) !== 'undefined') {
      var theme = localStorage.getItem('theme');
      if (!theme) {
        var hours = new Date().getHours();
        var dayTime = hours > 6 && hours < 20;
        if (!dayTime) this.toggleTheme('dark');
        return;
      }
      this.toggleTheme(theme);
      localStorage.setItem('theme', theme);
    }
  },


  setTableTheme() {
    /*
     * Set the appropriate theme for tables based on the current theme.
     */
    console.log('Setting theme on tables...');
    let nuisanceTableClass = 'ag-theme-alpine-dark';
    let finalTableClass = 'ag-theme-alpine';
    if (hasClass(document.body, 'dark')) {
      nuisanceTableClass = 'ag-theme-alpine';
      finalTableClass = 'ag-theme-alpine-dark';
    }
    // Toggle Ag-Grid theme.
    let tables = document.getElementsByClassName(nuisanceTableClass);
    [...tables].forEach( x => x.classList.add(finalTableClass) );
    [...tables].forEach( x => x.classList.remove(nuisanceTableClass) );
  },


  toggleTheme(theme) {
    /*
     * Toggle the UI theme, toggling AG-Grid table class.
     */
    let currentTableClass = 'ag-theme-alpine';
    let newTableClass = 'ag-theme-alpine-dark';
    if (theme === 'light') {
      document.body.className = 'base';
      currentTableClass = 'ag-theme-alpine-dark';
      newTableClass = 'ag-theme-alpine';
    } else {
      document.body.classList.add('dark');
    }
    // Toggle Ag-Grid theme.
    let tables = document.getElementsByClassName(currentTableClass);
    [...tables].forEach( x => x.classList.add(newTableClass) );
    [...tables].forEach( x => x.classList.remove(currentTableClass) );
  }


}

function hasClass(element, className) {
  return (' ' + element.className + ' ').indexOf(' ' + className + ' ') > -1;
}

