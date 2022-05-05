/**
 * Transfers JavaScript | Cannlytics Console
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors: Keegan Skeate <https://github.com/keeganskeate>
 * Created: 12/9/2020
 * Updated: 8/12/2021
 * License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>
 * 
 * Resources:
 *    https://github.com/fullcalendar/fullcalendar-example-projects/blob/master/webpack/src/main.js
 *    https://fullcalendar.io/docs/handlers
 */
// import { Calendar } from '@fullcalendar/core';
// import interactionPlugin from '@fullcalendar/interaction';
// import dayGridPlugin from '@fullcalendar/daygrid';
// import timeGridPlugin from '@fullcalendar/timegrid';
// import listPlugin from '@fullcalendar/list';
import { maps } from './map.js';

export const transfers = {

  ...maps,

  initialize() {
    /**
     * Initialize the transfers user interface.
     */
    // this.drawCalendar();
    var script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/fullcalendar@5.4.0/main.min.js';
    script.defer = true;
    // window.initMap = this.drawCalendar;
    document.head.appendChild(script);
    document.addEventListener('DOMContentLoaded', function() {
      var calendarEl = document.getElementById('calendar');
      var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        initialDate: '2020-12-07',
        headerToolbar: {
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        events: [
          {
            title: 'All Day Event',
            start: '2020-12-01'
          },
          {
            title: 'Long Event',
            start: '2020-12-07',
            end: '2020-12-10'
          },
          {
            groupId: '999',
            title: 'Repeating Event',
            start: '2020-12-09T16:00:00'
          },
          {
            groupId: '999',
            title: 'Repeating Event',
            start: '2020-12-16T16:00:00'
          },
          {
            title: 'Conference',
            start: '2020-12-11',
            end: '2020-12-13'
          },
          {
            title: 'Meeting',
            start: '2020-12-12T10:30:00',
            end: '2020-12-12T12:30:00'
          },
          {
            title: 'Lunch',
            start: '2020-12-12T12:00:00'
          },
          {
            title: 'Meeting',
            start: '2020-12-12T14:30:00'
          },
          {
            title: 'Birthday Party',
            start: '2020-12-13T07:00:00'
          },
          {
            title: 'Click for Google',
            url: 'http://google.com/',
            start: '2020-12-28'
          }
        ]
      });
      calendar.render();
    });
  },

  initializeLogs() {
    /**
     * Initialize transfer logs.
     */
    console.log('Initialize logs...');
  },

  initializeAnalytics() {
    /**
     * Initialize transfer analytics.
     */
    console.log('Initialize analytics...');
  },

  drawCalendar() {
    /**
     * Draw the transfer calendar.
     */
    var calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;
    var calendar = new Calendar(calendarEl, {
      plugins: [ interactionPlugin, dayGridPlugin, timeGridPlugin, listPlugin ],
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
      },
      initialDate: '2020-12-10', // TODO: Set current day.
      navLinks: true, // can click day/week names to navigate views
      editable: true,
      dayMaxEvents: true, // allow "more" link when too many events
      // TODO: Get events from Firestore.
      events: [
        {
          title: 'Meeting',
          start: '2020-12-12T10:30:00',
          end: '2020-12-12T12:30:00'
        },
      ],
      dateClick: function() {
        console.log('a day has been clicked!');
      },
    });
    calendar.render();
  },

  drawMap() {
    /**
     * Draw the transfer map.
     */
    var locations = [["USA", 39.8283, -98.5795, 1]]; // TODO: Get location of transfers from Firestore
    var map = new google.maps.Map(document.getElementById('map'), {
      zoom: 4,
      center: new google.maps.LatLng(39.8283, -98.5795), // TODO: Get organization's latitude and longitude
      mapTypeId: google.maps.MapTypeId.ROADMAP
    });
    var infoWindow = new google.maps.InfoWindow();
    var marker, i;
    for (i = 0; i < locations.length; i++) {
      marker = new google.maps.Marker({
        position: new google.maps.LatLng(locations[i][1], locations[i][2]),
        map: map
      });
      google.maps.event.addListener(marker, 'click', (function(marker, i) {
        return function() {
          infoWindow.setContent(locations[i][0]);
          infoWindow.open(map, marker);
        }
      })(marker, i));
    }
  },

};
