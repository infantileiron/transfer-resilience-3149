export const number=(v:number|null|undefined,d=2)=>v==null?'不适用':v.toFixed(d);
export const travel=(v:number|null|undefined)=>v==null?'不可达':v.toFixed(2)+' 分钟';
export const date=(v:string)=>new Date(v).toLocaleString('zh-CN',{hour12:false});
