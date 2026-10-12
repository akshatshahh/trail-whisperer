// @vitest-environment jsdom
import React from 'react';
import {afterEach,beforeEach,describe,it,expect,vi} from 'vitest';
import {render,screen,fireEvent,cleanup,waitFor} from '@testing-library/react';
import PhotoCapture from './PhotoCapture';
afterEach(()=>{cleanup();vi.restoreAllMocks()});
beforeEach(()=>{Object.defineProperty(navigator,'maxTouchPoints',{configurable:true,value:0});Object.defineProperty(window,'isSecureContext',{configurable:true,value:true})});
describe('photo capture regression',()=>{
 it('offers native camera capture on phones without requiring getUserMedia',()=>{
  Object.defineProperty(navigator,'maxTouchPoints',{configurable:true,value:5});
  const getUserMedia=vi.fn();Object.defineProperty(navigator,'mediaDevices',{configurable:true,value:{getUserMedia}});
  const click=vi.spyOn(HTMLInputElement.prototype,'click').mockImplementation(()=>{});
  render(<PhotoCapture onFile={vi.fn()} onClose={vi.fn()}/>);
  fireEvent.click(screen.getByRole('button',{name:'Take photo'}));
  expect(click).toHaveBeenCalledOnce();expect(getUserMedia).not.toHaveBeenCalled();
  expect(document.querySelector('input[capture]').getAttribute('capture')).toBe('environment');
 });
 it('uploads an existing image and closes the dialog',()=>{
  const onFile=vi.fn(),onClose=vi.fn();render(<PhotoCapture onFile={onFile} onClose={onClose}/>);
  const file=new File(['test'],'plant.jpg',{type:'image/jpeg'});
  fireEvent.change(document.querySelector('input:not([capture])'),{target:{files:[file]}});
  expect(onFile).toHaveBeenCalledWith(file);expect(onClose).toHaveBeenCalledOnce();
 });
 it('does not close or identify when the picker is canceled',()=>{
  const onFile=vi.fn(),onClose=vi.fn();render(<PhotoCapture onFile={onFile} onClose={onClose}/>);
  fireEvent.change(document.querySelector('input[capture]'),{target:{files:[]}});
  expect(onFile).not.toHaveBeenCalled();expect(onClose).not.toHaveBeenCalled();
 });
 it('keeps upload available on insecure desktop HTTP',()=>{
  Object.defineProperty(window,'isSecureContext',{configurable:true,value:false});render(<PhotoCapture onFile={vi.fn()} onClose={vi.fn()}/>);
  fireEvent.click(screen.getByRole('button',{name:'Take photo'}));
  expect(screen.getByRole('alert').textContent).toContain('HTTPS');expect(screen.getByRole('button',{name:'Upload photo'}).disabled).toBe(false);
 });
 it('recovers gracefully when webcam permission is denied',async()=>{
  Object.defineProperty(navigator,'mediaDevices',{configurable:true,value:{getUserMedia:vi.fn().mockRejectedValue(new Error('denied'))}});
  render(<PhotoCapture onFile={vi.fn()} onClose={vi.fn()}/>);fireEvent.click(screen.getByRole('button',{name:'Take photo'}));
  await waitFor(()=>expect(screen.getByRole('alert').textContent).toContain('permission denied'));
  expect(screen.getByRole('button',{name:'Take photo'}).disabled).toBe(false);
 });
 it('stops webcam tracks when dismissed',async()=>{
  const stop=vi.fn();Object.defineProperty(navigator,'mediaDevices',{configurable:true,value:{getUserMedia:vi.fn().mockResolvedValue({getTracks:()=>[{stop}]})}});
  const {unmount}=render(<PhotoCapture onFile={vi.fn()} onClose={vi.fn()}/>);fireEvent.click(screen.getByRole('button',{name:'Take photo'}));
  await screen.findByRole('button',{name:'Capture photo'});unmount();expect(stop).toHaveBeenCalledOnce();
 });
 it('stops a camera that resolves after the dialog has closed',async()=>{
  let resolve;const stop=vi.fn();Object.defineProperty(navigator,'mediaDevices',{configurable:true,value:{getUserMedia:vi.fn(()=>new Promise(r=>{resolve=r}))}});
  const {unmount}=render(<PhotoCapture onFile={vi.fn()} onClose={vi.fn()}/>);fireEvent.click(screen.getByRole('button',{name:'Take photo'}));unmount();resolve({getTracks:()=>[{stop}]});await waitFor(()=>expect(stop).toHaveBeenCalledOnce());
 });
});
