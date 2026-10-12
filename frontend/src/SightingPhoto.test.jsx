// @vitest-environment jsdom
import React from 'react';
import {afterEach,it,expect} from 'vitest';
import {render,screen,fireEvent,cleanup} from '@testing-library/react';
import SightingPhoto from './SightingPhoto';
afterEach(cleanup);
it('shows a fallback when the image request fails',()=>{
 render(<SightingPhoto src="/media/missing.jpg" label="Squirrel" kind="mammal"/>);
 fireEvent.error(screen.getByAltText('Squirrel'));
 expect(screen.queryByAltText('Squirrel')).toBeNull();
 expect(screen.getByLabelText('Photo unavailable')).toBeTruthy();
});
it('tries the new image after a missing path is repaired',()=>{
 const {rerender}=render(<SightingPhoto src="/media/missing.jpg" label="Squirrel" kind="mammal"/>);
 fireEvent.error(screen.getByAltText('Squirrel'));
 rerender(<SightingPhoto src="/media/found.jpg" label="Squirrel" kind="mammal"/>);
 expect(screen.getByAltText('Squirrel').getAttribute('src')).toBe('/media/found.jpg');
});
