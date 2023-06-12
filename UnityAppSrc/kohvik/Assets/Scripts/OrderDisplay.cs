using System.Collections;
using System.Linq;
using TMPro;
using UnityEngine;
using UnityEngine.Networking;

public class OrderDisplay : MonoBehaviour
{
    [SerializeField] GameObject orderPrefab;
    private OrderList orders;
    private float timePassed = 0f;

    void Start()
    {
        StartCoroutine(GetOrders());
    }

    private IEnumerator GetOrders()
    {
        UnityWebRequest www = UnityWebRequest.Get($"{Constants.IP}/getReadyOrders");
        yield return www.SendWebRequest();
        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            string jsonResponse = www.downloadHandler.text;
            orders = JsonUtility.FromJson<OrderList>("{\"Orders\":" + jsonResponse + "}");
            foreach (Order order in orders.Orders)
            {
                order.orderObject = Instantiate(orderPrefab, new Vector3(0, 0, 0), Quaternion.identity);
                order.orderObject.transform.SetParent(transform, false);
                order.orderObject.transform.GetChild(0).GetComponent<TMP_Text>().SetText(order.ID.ToString());
            }
        }
    }

    private IEnumerator UpdateOrders()
    {
        OrderList temp_orders;
        UnityWebRequest www = UnityWebRequest.Get($"{Constants.IP}/getReadyOrders");
        yield return www.SendWebRequest();
        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            string jsonResponse = www.downloadHandler.text;
            temp_orders = JsonUtility.FromJson<OrderList>("{\"Orders\":" + jsonResponse + "}");
            foreach (Order order in orders.Orders.Except(temp_orders.Orders).ToList())
            {
                order.orderObject.SetActive(false);
                orders.Orders.Remove(order);
                Destroy(order.orderObject, 3f);
            }

            foreach (Order order in temp_orders.Orders.Except(orders.Orders).ToList())
            {
                order.orderObject = Instantiate(orderPrefab, new Vector3(0, 0, 0), Quaternion.identity);
                order.orderObject.transform.SetParent(transform, false);
                order.orderObject.transform.GetChild(0).GetComponent<TMP_Text>().SetText(order.ID.ToString());
                orders.Orders.Add(order);
            }
        }

    }

    // Update is called once per frame
    void Update()
    {
        timePassed += Time.deltaTime;
        if (timePassed > 2f)
        {
            StartCoroutine(UpdateOrders());
            timePassed = 0f;
        }
    }
}
