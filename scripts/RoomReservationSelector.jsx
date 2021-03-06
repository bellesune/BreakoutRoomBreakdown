import * as React from 'react';

export default function RoomReservationSelector(props) {
  const minAttendeeCount = 2;
  const maxAttendeeCount = 12;
  const { setAttendeeCount } = props;

  function updateAttendeeCount(event) {
    setAttendeeCount(parseInt(event.target.value));
  }

  return (
    <div>
      <label htmlFor="studentCount">Number of students (including you)</label>
      <select
        name="studentCount"
        id="studentCount"
        defaultValue="0"
        onChange={updateAttendeeCount}
      >
        <option disabled hidden value="0"> - </option>
        {
                    [...Array(maxAttendeeCount - minAttendeeCount + 1).keys()].map(
                      (index) => {
                        const value = index + minAttendeeCount;
                        return <option value={value} key={value}>{value}</option>;
                      },
                    )
                }
      </select>
    </div>
  );
}
