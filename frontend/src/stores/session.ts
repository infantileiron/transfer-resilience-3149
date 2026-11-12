import type {User} from '../types/domain';
export function readUser():User|null{try{return JSON.parse(localStorage.getItem('transfer-user')||'null')}catch{return null}}
export function save(token:string,user:User){localStorage.setItem('transfer-token',token);localStorage.setItem('transfer-user',JSON.stringify(user))}
export function clear(){localStorage.removeItem('transfer-token');localStorage.removeItem('transfer-user')}
