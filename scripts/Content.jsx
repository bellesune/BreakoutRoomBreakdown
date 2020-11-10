import * as React from 'react';

import { GoogleButton } from './GoogleButton';
import { RoomReservation } from './RoomReservation';
import { Submit } from './Submit';

export function Content() {
    return (
        <div>
            <h1>Log in with OAuth!</h1>
            <GoogleButton />
            <RoomReservation />
            <Submit />
        </div>
    );
}
