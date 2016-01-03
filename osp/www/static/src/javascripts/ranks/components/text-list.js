

import _ from 'lodash';
import React, { Component, PropTypes } from 'react';

import Search from './search';
import TextRow from './text-row';


export default class extends Component {


  static propTypes = {
    totalHits: PropTypes.number.isRequired,
    hits: PropTypes.array.isRequired,
  }


  /**
   * Render the ranking table.
   */
  render() {

    // Format the count.
    let totalHits = this.props.totalHits.toLocaleString();

    // Build the text list.
    let rows = _.map(this.props.hits, function(h, i) {
      return <TextRow key={h._id} hit={h} rank={i+1} />
    });

    return (
      <div id="text-list">

        <div className="list-header">

          <div className="total-hits">
            <span className="count">{totalHits}</span>{' '}
            <span className="texts">texts</span>
          </div>

          <Search />

        </div>

        <table className="table table-hover">

          <thead>
            <tr>
              <th>Rank</th>
              <th>Count</th>
              <th>Text</th>
            </tr>
          </thead>

          <tbody>
            {rows}
          </tbody>

        </table>

      </div>
    );

  }


}