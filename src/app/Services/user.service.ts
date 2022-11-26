import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, Observable, retry, throwError } from 'rxjs';
import { Constant } from '../Utilities/Constant';
import { Movies } from '../Utilities/Movie';
import { people } from '../Utilities/people';
import { ApiConsumingService } from './api-consuming.service';


@Injectable({
  providedIn: 'root'
})
export class UserService {

  constructor(private router:Router,private httpclient:HttpClient,private apiservice:ApiConsumingService) { }

  addUser(user:any){
    let users=[];
    if(localStorage.getItem('Users')){
     users=JSON.parse(localStorage.getItem('Users')||'{}');
     users=[user,...users];
    }
    else{
     users=[user];
    }
    localStorage.setItem('Users',JSON.stringify(users));
   }

   updateTickets(data:any,id:any):Observable<any>{
     const header=new HttpHeaders();
     header.set('Content-Type','application/json');
     return this.httpclient.put<Movies>(`${Constant.updateEndPoint}/${id}`,data,{ 'headers': header }).pipe(retry(1),catchError(this.handleError));
   }
   
   updateTicketsByUpdatedUser(data:any,id:any):Observable<any>{
    const header=new HttpHeaders();
    header.set('Content-Type','application/json');
    console.log("updated data=",data);
    return this.httpclient.put<Movies>(`${Constant.updateEndPoint}/${id}`,data,{ 'headers': header }).pipe(retry(1),catchError(this.handleError));

   }

   handleError(err:any){
    return throwError(()=>{
      console.log(err);
    });
  }
 
}
