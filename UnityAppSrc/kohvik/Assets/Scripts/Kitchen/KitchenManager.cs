using System.Collections;
using TMPro;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using System.Linq;

public class KitchenManager : MonoBehaviour
{
    [SerializeField] ToggleGroup toggleGroup;
    [SerializeField] string orderType;
    [SerializeField] GameObject orderPrefab;
    public GameObject confirmBox;
    public GameObject messageBox;
    private TMP_Text messageBoxText;
    private TMP_Text confirmBoxText;
    private Order currentOrder;
    private OrderList orders;
    float timePassed = 0f;
    private WWWForm form;

    // Start is called before the first frame update
    void Awake()
    {
        messageBoxText = messageBox.transform.GetChild(0).Find("MessageText").GetComponent<TMP_Text>();
        confirmBoxText = confirmBox.transform.GetChild(0).Find("ConfirmText").GetComponent<TMP_Text>();
        StartCoroutine(GetOrders());
    }

    private IEnumerator GetOrders()
    {
        UnityWebRequest www = UnityWebRequest.Get($"{Constants.IP}/{orderType}");
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
                order.orderObject.SetActive(false);
                order.orderObject.GetComponent<OrderButton>().SetOrder(order);
                order.orderObject.transform.SetParent(transform, false);
                order.orderObject.transform.GetChild(0).GetComponent<Toggle>().group = toggleGroup;
                StartCoroutine(GetItems(order));
            }
        }
    }

    private IEnumerator GetItems(Order order)
    {
        UnityWebRequest www = UnityWebRequest.Get($"{Constants.IP}/getOrderedItems/{order.ID}");
        yield return www.SendWebRequest();
        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            string jsonResponse = www.downloadHandler.text;
            ItemList items = JsonUtility.FromJson<ItemList>("{\"Items\":" + jsonResponse + "}");
            order.items = items.Items;
            Debug.Log(order.ID);
            
            string orderText = "NR " + order.ID + ": ";
            foreach (Item item in order.items)
            {
                orderText += item.Count + " " + item.Name + " ";
            }
            order.orderObject.transform.GetChild(0).GetChild(0).GetComponent<TMP_Text>().SetText(orderText);
            order.orderObject.SetActive(true);
        }
    }

    private IEnumerator UpdateOrders()
    {
        OrderList temp_orders;
        UnityWebRequest www = UnityWebRequest.Get($"{Constants.IP}/{orderType}");
        yield return www.SendWebRequest();
        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            string jsonResponse = www.downloadHandler.text;
            temp_orders = JsonUtility.FromJson<OrderList>("{\"Orders\":" + jsonResponse + "}");

            foreach (Order order in orders.Orders.Except(temp_orders.Orders).ToList()) {
                order.orderObject.SetActive(false);
                orders.Orders.Remove(order);
                Destroy(order.orderObject, 3f);
            }

            foreach (Order order in temp_orders.Orders.Except(orders.Orders).ToList())
            {
                order.orderObject = Instantiate(orderPrefab, new Vector3(0, 0, 0), Quaternion.identity);
                order.orderObject.SetActive(false);
                order.orderObject.GetComponent<OrderButton>().SetOrder(order);
                order.orderObject.transform.SetParent(transform, false);
                order.orderObject.transform.GetChild(0).GetComponent<Toggle>().group = toggleGroup;
                orders.Orders.Add(order);
                StartCoroutine(GetItems(order));
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

    public void OnHandOverPressed()
    {
        var button = toggleGroup.GetFirstActiveToggle();
        if (button == null)
        {
            Debug.Log("no item selected.");
            return;
        }
        currentOrder = button.GetComponentInParent<OrderButton>().GetOrder();
        form = new();
        form.AddField("status", 2);
        messageBoxText.SetText($"Olete kindel, et soovite tellimuse {currentOrder.ID} üle anda?");
        messageBox.SetActive(true);
    }

    public void OnCompletePressed()
    {
        var button = toggleGroup.GetFirstActiveToggle();
        if (button == null)
        {
            Debug.Log("no item selected.");
            return;
        }
        currentOrder = button.GetComponentInParent<OrderButton>().GetOrder();
        form = new();
        form.AddField("status", 1);
        messageBoxText.SetText($"Olete kindel, et soovite märkida tellimuse {currentOrder.ID} valminuks?");
        messageBox.SetActive(true);
    }

    public void ConfirmOrderStatus()
    {
        StartCoroutine(Upload(form));
    }

    IEnumerator Upload(WWWForm formData)
    {
        UnityWebRequest www = UnityWebRequest.Post($"{Constants.IP}/updateOrder/{currentOrder.ID}", formData);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
            confirmBoxText.SetText("Tellimuse edastamine ebaõnnestus. Proovi uuesti ja/või kontrolli võrguühendust.");
        }
        else
        {
            string response = System.Text.Encoding.Default.GetString(www.downloadHandler.data);
            confirmBoxText.SetText(response.Trim());
        }
        confirmBox.SetActive(true);
        StartCoroutine(UpdateOrders());
        www.Dispose();
    }

}
