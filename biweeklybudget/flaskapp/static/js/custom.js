/*
The latest version of this package is available at:
<http://github.com/jantman/biweeklybudget>

################################################################################
Copyright 2016 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of biweeklybudget, also known as biweeklybudget.

    biweeklybudget is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    biweeklybudget is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with biweeklybudget.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/biweeklybudget> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
################################################################################
*/

/**
 * Format a null object as "&nbsp;"
 *
 * @param {(Object|null)} o - input value
 * @returns {(Object|string)} o if not null, ``&nbsp;`` if null
 */
function fmt_null(o) {
    if ( o === null ) {
        return '&nbsp;';
    }
    return o;
}

/**
 * Format a float as currency
 *
 * @param {number} value - the number to format
 * @returns {string} The number formatted as currency
 */
function fmt_currency(value) {
    if (value === null) { return '&nbsp;'; }
    return '$' + value.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,")
}

/**
 * Format a dtdict as returned by
 * :py:class:`biweeklybudget.flaskapp.jsonencoder.MagicJSONEncoder`
 * in ``%Y-%m-%d`` format.
 *
 * @param {Object} d - date dict
 * @returns {string} formatted Y-m-d date
 */
function fmt_dtdict_ymd(d) {
    var ds = d['date'] + '';
    var ms = d['month'] + '';
    if (ds.length < 2) { ds = '0' + ds; }
    if (ms.length < 2) { ms = '0' + ms; }
    return d['year'] + '-' + ms + '-' + ds;
}

/**
 * Format a javascript Date as ISO8601 YYYY-MM-DD
 *
 * @param {Date} d - the date to format
 * @returns {string} YYYY-MM-DD
 */
function isoformat(d) {
  var mm = d.getMonth() + 1; // getMonth() is zero-based
  var dd = d.getDate();

  return [d.getFullYear(),
          (mm>9 ? '' : '0') + mm,
          (dd>9 ? '' : '0') + dd
         ].join('-');
}
