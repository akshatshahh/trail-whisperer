import React,{useEffect,useRef,useState} from 'react';
import {Camera,Upload,X} from 'lucide-react';
export default function PhotoCapture({onClose,onFile}){
 const video=useRef(),native=useRef(),upload=useRef(),stream=useRef(),closed=useRef(false);
 const [live,setLive]=useState(false),[error,setError]=useState(''),[opening,setOpening]=useState(false);
 useEffect(()=>()=>{closed.current=true;stream.current?.getTracks().forEach(t=>t.stop())},[]);
 useEffect(()=>{if(live&&video.current)video.current.srcObject=stream.current},[live]);
 function chosen(file){if(file){onFile(file);onClose()}}
 async function start(){
  if(navigator.maxTouchPoints>0){native.current.click();return}
  if(!window.isSecureContext||!navigator.mediaDevices?.getUserMedia){setError('Live camera needs HTTPS or localhost. You can still upload a photo.');return}
  setOpening(true);setError('');
  try{const s=await navigator.mediaDevices.getUserMedia({video:{facingMode:{ideal:'environment'}},audio:false});if(closed.current){s.getTracks().forEach(t=>t.stop());return}stream.current=s;setLive(true)}
  catch{setError('Camera unavailable or permission denied. Choose a photo below.')}finally{setOpening(false)}
 }
 function snap(){const v=video.current;if(!v?.videoWidth){setError('Camera is still loading. Try again in a moment.');return}const canvas=document.createElement('canvas');canvas.width=v.videoWidth;canvas.height=v.videoHeight;canvas.getContext('2d').drawImage(v,0,0);canvas.toBlob(b=>{if(b)chosen(new File([b],'camera-photo.jpg',{type:'image/jpeg'}))},'image/jpeg',.9)}
 return <div className="modal-backdrop"><section className="modal" role="dialog" aria-modal="true" aria-labelledby="photo-title"><button className="close" onClick={onClose} aria-label="Close camera"><X/></button><p className="eyebrow">LOOK CLOSER</p><h2 id="photo-title">Identify a photo.</h2><p>Photograph a plant or animal, or choose a picture you already have.</p>{live&&<video className="camera-preview" ref={video} autoPlay playsInline muted/>}{error&&<p role="alert" className="caution">{error}</p>}<div className="photo-actions"><button className="primary" onClick={live?snap:start} disabled={opening}><Camera size={18}/>{opening?'Opening camera…':live?'Capture photo':'Take photo'}</button><button className="outline" onClick={()=>upload.current.click()}><Upload size={18}/>Upload photo</button></div><p className="small muted">Identification runs on this server’s local Gemma model. Review the result before saving.</p><input ref={native} type="file" accept="image/*" capture="environment" hidden onChange={e=>chosen(e.target.files[0])}/><input ref={upload} type="file" accept="image/jpeg,image/png,image/webp" hidden onChange={e=>chosen(e.target.files[0])}/></section></div>
}
