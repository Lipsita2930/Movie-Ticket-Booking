import { Injectable } from '@angular/core';
import{HttpClient} from '@angular/common/http';
import { Movies } from '../Utilities/Movie';
import { Constant } from '../Utilities/Constant';
import {Observable,retry,throwError,catchError} from 'rxjs';
import { Router } from '@angular/router';
@Injectable({
  providedIn: 'root'
})
export class ApiConsumingService {
  

  constructor(private httpClient:HttpClient) { }


  getMovieDetails():Observable<Movies[]>{
    return this.httpClient.get<Movies[]>(Constant.getEndPoint.toString()).
    pipe(retry(1),catchError(this.handleError));
  }
  getMovieDetailsById(id:any):Observable<any>{
    return this.httpClient.get<any>(`${Constant.updateEndPoint}/${id}`).
    pipe(retry(1),catchError(this.handleError));
  }
  handleError(err:any){
    return throwError(()=>{console.log(err);})
  }

}
