/**
 * User Interface JavaScript | Cannlytics Console
 * Licensed under GPLv3 (https://github.com/cannlytics/cannlytics_console/blob/main/LICENSE)
 * Author: Keegan Skeate <contact@cannlytics.com>
 * Created: 5/2/2021
 */

export const ui = {

  hideSidebar() {
    /*
     * Hides the console sidebar.
     */
    const sidebar = document.getElementById('sidebar-menu');
    const sidebarToggle = document.getElementById('sidebar-console-toggle');
    sidebar.classList.add('d-none');
    sidebar.classList.remove('d-md-block');
    sidebarToggle.classList.remove('d-md-none');
  },


  showSidebar() {
    /*
     * Show the console sidebar.
     */
    const sidebar = document.getElementById('sidebar-menu');
    const sidebarToggle = document.getElementById('sidebar-console-toggle');
    sidebar.classList.remove('d-none');
    sidebar.classList.add('d-md-block');
    sidebarToggle.classList.add('d-md-none');
  },


  addListItem(type) {
    /*
     * Adds a list item of input fields to the UI by
     * cloning the primary list item and clearing its fields.
     * The delete button is shown and wired-up.
     * The tooltip is removed.
     */
    var ul = document.getElementById(`${type}-list`);
    var li = document.getElementById(`primary-${type}`).cloneNode(true);
    var id = `${type}-${ul.children.length + 1}`;
    li.setAttribute('id', id);
    ul.appendChild(li);
    $(`#${id} input`).val('');
    $(`#${id} .btn-tooltip-help`).remove();
    var deleteButton = $(`#${id} .btn-link`);
    deleteButton.removeClass('d-none');
    deleteButton.attr('onClick', `cannlytics.ui.removeListItem(event, '${type}-list', '${id}');`);
  },


  removeListItem(event, listId, elementId) {
    /*
     * Remove an element from a list.
     */
    event.preventDefault();
    var ul = document.getElementById(listId);
    var item = document.getElementById(elementId);
    ul.removeChild(item);
  },


  toggleElementClass(id, className) {
    /*
     * Show or hide a given element.
     */
    const element = document.getElementById(id);
    element.classList.toggle(className);
  },


  showLoadingButton(buttonId) {
    /*
     * Show a hidden loading button given the ID of its button counterpart.
     */
    document.getElementById(buttonId).classList.add('d-none');
    document.getElementById(`${buttonId}-loading`).classList.remove('d-none');
  },


  hideLoadingButton() {
    /*
     * Hide a by-default hidden loading button given the ID of its button counterpart.
     */
    document.getElementById(buttonId).classList.add('d-none');
    document.getElementById(`${buttonId}-loading`).classList.remove('d-none');
  },


}
