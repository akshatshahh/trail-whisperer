import React,{useEffect,useState} from 'react';
import {Bird,Leaf,Compass,Headphones} from 'lucide-react';
const icons={bird:Bird,plant:Leaf,mammal:Compass,journal:Headphones,other:Leaf};
export default function SightingPhoto({src,label,kind}){
 const [failed,setFailed]=useState(false);
 useEffect(()=>setFailed(false),[src]);
 const Icon=icons[kind]||Leaf;
 return src&&!failed?<img src={src} alt={label} onError={()=>setFailed(true)}/>:<><Icon size={62} strokeWidth={1} aria-label={failed?'Photo unavailable':'No photo'}/><span className="art-ring"/></>;
}
