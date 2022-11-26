import { environment } from "src/environments/environment";
export module Constant{
    const baseUrl:String=environment.baseURL;
    export const getEndPoint:String=`${baseUrl}`;
    export const updateEndPoint:String=`${baseUrl}/`;
    export const getEndPointById:String=`${baseUrl}/`;
}
